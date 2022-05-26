#!/usr/bin/env python3

import re, sys, time, getopt
from datetime import datetime
from ragu_http import getHttpContent
from ragu_file import writeCsv,readCsv
from bs4 import BeautifulSoup

global frontpage
frontpage='https://www.romhacking.net/'

global address_first
address_first='https://www.romhacking.net/hacks/'

def usage():
    print("rhdn_tabler2.py -- scrape each hack page on romhacking.net and output a tsv")
    print("-i,--input=[filename]\t\tinput file, to update an existing tsv from previous scrape.")
    print("-o,--output=[filename]\t\toutput file, if nothing set, will use rhdn_hacks.csv")
    print("-h,--help\t\t\tthis message")
    print("")


def getHTML(address):
    retry=0
    while retry <= 5:
        try:
            http_get=getHttpContent(address)
            http_response=http_get['response']
            http_content=BeautifulSoup(''.join(http_get['content']),"html.parser")
            return(http_content,http_response)
        except Exception as e:
            err=e
            time.sleep(30)
            retry+=1
    
    raise(err)

def modCoder(mods):
    mod_list=mods.split("/")
    mod_int=0
    for mod in mod_list:
        if mod == "G":
            mod_int+=1
        elif mod == "L":
            mod_int+=2
        elif mod == "T":
            mod_int+=4
        elif mod == "S":
            mod_int+=8
        elif mod == "GP":
            mod_int+=16
        elif mod == "Other":
            mod_int+=32

    return(mod_int)


def getMaxRange():
    html_content, http_response=getHTML(frontpage)
    return(int(re.sub(r'^\/hacks\/([0-9]+)\/',r'\1',html_content.find('div', id='rightbar').findAll('div', class_="newsitem")[0].findAll('div', class_="column_link")[0].a['href'])))
        
def getALink(content):
    content=re.sub(r'  +',r' ',str(content))
    if "a href" in str(content).lower():
        a_link=BeautifulSoup(''.join(content),"html.parser")
        return(a_link.a.contents[0])
    else:
        return(content)

def getReadme(content):
    content=re.sub(r'  +',r' ',str(content))
    if "a href" in str(content).lower():
        a_link=BeautifulSoup(''.join(content),"html.parser")
        return(a_link.a['href'])
    else:
        return(content)

def convTime(datestring):
    date_time=datetime.strptime(datestring, "%d %B %Y")
    converted_time=date_time.strftime("%Y-%m-%d")
    return(converted_time)

def parseSidebar(url):
    output_list=["","","","","","","","","","","","","","",""]
    html_content, http_response=getHTML(url)
    if http_response.status != 200:
        if http_response.status == 301:
            return(1)
        else:
            raise("Unknown HTTP response: " + http_response.status)
        

    info_sidebar=html_content.find('table', class_="entryinfo")


    # parse the table rows
    try:
        table_rows=info_sidebar.find_all('tr')[0:]
    except AttributeError as err:
        error_msg=html_content.find('div',id='main').find('div',class_='newsbody').contents[0]
        if "Hack does not exist" in str(error_msg):
            return(1)
    except Exception as err:
        raise(err)

    # hack title
    output_list[0]=table_rows[0].find_all('div')[1].contents[0]


    # game title
    game_title=table_rows[0].find_all('div')[2].a.contents[0]
    output_list[1]=re.sub(r'^The (.*)$',r'\1, The',game_title)

    # now we grab the rest
    for tr in table_rows[1:]:
        field=tr.th.contents[0]
        contents=tr.td.contents[0]
        if field == "Released By":
            output_list[2]=getALink(contents)
        elif field == "Category":
            output_list[3]=getALink(contents)
        elif field == "Platform":
            output_list[4]=getALink(contents)
        elif field == "Genre":
            output_list[5]=getALink(contents)
        elif field == "Mods":
            output_list[6]=(getALink(contents)).replace(',','/')
            output_list[7]=modCoder(getALink(contents))
        elif field == "Patch Version":
            output_list[8]=getALink(contents)
        elif field == "Hack Release Date":
            output_list[9]=convTime(getALink(contents))
        elif field == "Readme":
            output_list[10]="=HYPERLINK(\""+getReadme(contents)+"\")"
        elif field == "Last Modified":
            output_list[11]=convTime(getALink(contents))


    # append url to list
    output_list[12]="=HYPERLINK(\""+url+"\")"


    return(output_list)


def updateRow(input_csv,output_list,url):
    # get the row that matches the url from the input csv
    new_output_list=["","","","","","","","","","","","","","",""]
    old_row = next((item for item in input_csv if item["url"] == url),None)
    # if it can't find a matching url, do nothing and just return the output list
    if old_row == None:
        return(output_list)
    # check if the modified date is different on the output list, then add get_status and modified cols to create new_output_list, return
    elif old_row["last_modified"] != output_list[11]:
        new_output_list=output_list
        new_output_list[13]=old_row["get_status"]
        new_output_list[14]="Y"
        return(new_output_list)
    # otherwise, create new_output_list from old_row
    else:
        new_output_list[0]=old_row["hack_title"]
        new_output_list[1]=old_row["original_title"]
        new_output_list[2]=old_row["author"]
        new_output_list[3]=old_row["category"]
        new_output_list[4]=old_row["platform"]
        new_output_list[5]=old_row["genre"]
        new_output_list[6]=old_row["mods"]
        new_output_list[7]=old_row["mod_code"]
        new_output_list[8]=old_row["patch_ver"]
        new_output_list[9]=old_row["release_date"]
        new_output_list[10]="=HYPERLINK(\""+old_row["readme"]+"\")"
        new_output_list[11]=old_row["last_modified"]
        new_output_list[12]="=HYPERLINK(\""+old_row["url"]+"\")"
        new_output_list[13]=old_row["get_status"]
        new_output_list[14]=old_row["updated"]
        return(new_output_list)
    

def main(argv):
    header=["hack_title","original_title","author","category","platform","genre","mods","mod_code","patch_ver","release_date","readme","last_modified","url","get_status","updated"]
    csv_list=[]
    input_file=""
    filename=""

    try:
        opts, args = getopt.getopt(argv,"hi:o:",["input=","output="])
    except getopt.GetoptError:
        usage()
        raise(getopt.GetoptError("Invalid option",))
    for opt, arg in opts:
        if opt == '-h':
            usage()
            sys.exit()
        elif opt in ("-i", "--ifile"):
            input_file = arg
            try:
                input_csv=readCsv(input_file,"\t")
            except FileNotFoundError:
                raise FileNotFoundError("Input file "+input_file+" not found")
            except IndexError:
                raise IndexError("Input file "+input_file+" could not be read as a tab-separated csv file")
            except PermissionError:
                raise PermissionError("Unable to read input file "+input_file+" due to permissions restrictions")
            except Exception as e:
                raise Exception("Unknown error opening input file "+input_file+": "+e)
        elif opt in ("-o", "--ofile"):
            filename = arg
    
    
    # first, get max range from front page
    max_range=getMaxRange()
    for i in range(1,max_range+1):
        output_list=[]
        url=address_first + str(i)
        print(url)
        output_list=parseSidebar(url)
        if output_list == 1:
            continue
        # if we are updating an old list, compare
        if input_file != "":
            output_list=updateRow(input_csv,output_list,url)
        csv_list.append(output_list)
      

    if (len(args) == 0) or (not type(args[0]) == str) or (len(args[0]) == 0):
        filename='rhdn_hacks.csv'
    else:
        filename=args[0]

    try:
        writeCsv(filename,header,csv_list,"\t",True)
    except FileExistsError:
        raise FileExistsError("Output file "+filename+" ")
    except PermissionError:
        raise PermissionError("Input file "+filename+" could not be written to due to permissions restrictions")
    except Exception as e:
        raise Exception("Unknown error writing to output file "+filename+" : "+e)



if __name__ == "__main__":
    main(sys.argv[1:])
