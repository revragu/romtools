#!/usr/bin/env python3

import re, csv
from ragu_http import getHttpContent
from bs4 import BeautifulSoup

global address_first
address_first='https://www.romhacking.net/?page=hacks&platform='
global address_second
address_second='&perpage=200&startpage='


def getHTML(address):
    http_get=getHttpContent(address)
    http_content=BeautifulSoup(''.join(http_get['content']),"html.parser")
    return(http_content)


def getPlatforms():
    platforms=[]
    address=address_first + '1' + '&perpage=10&startpage=' + '1'
    http_content=getHTML(address)
    select_tag=http_content.find('select',id="platform")
    options_tags=select_tag.findAll('option')
    for i in options_tags:
        platform={}
        val=i['value']
        content=i.contents[0]
        try:
            platform['id']=int(val)
            platform['name']=str(content)
            platforms.append(platform)
        except:
            pass
    return(platforms)


def getPages(platform):
    pages=[]
    address=address_first + str(platform) + address_second + '1'
    http_content=getHTML(address)
    hack_pages_div=http_content.find('div', class_="pages")
    hack_pages=hack_pages_div.findAll('a')
    for i in hack_pages:
        
        try:
            val=int(i.contents[0])
            pages.append(val)
        except:
            pass
    pages.sort(reverse=True)
    try:
        return(pages[0])
    except:
        return(1)



def getTable(platform,page):
    address=address_first + str(platform) + address_second + str(page)
    http_content=getHTML(address)
    hack_table=http_content.find('table')
    return(hack_table)
    
def getHeader(header_row):
    header=[]
    cols=header_row.findAll('th')
    for i in cols:
        try:
            out=i.find('a')
            header.append(out.contents[0])    
        except:
            header.append(i.contents[0])
    header.append('Link')
    return(header)

def getRow(row):
    output_row=[]
    cols=row.findAll('td')
    for i in cols:
        if i['class'][0] == "col_1":
            link=i.find('a')
            link_href='https://www.romhacking.net' + str(link['href'])
            output_row.append(link.contents[0])
        else:
            try:
                link=i.find('a')
                output_row.append(link.contents[0])
            except:
                output_row.append(i.contents[0])
    output_row.append(link_href)
    return(output_row)


        

platforms=getPlatforms()
#platforms=[{'id':1,'name':'NES'}]
for platform in platforms:
    platform_name=(platform['name'].replace(' ','_')).replace('/','_')
    plat_id=platform['id']
    all_rows=[]
    print("Platform:",platform_name + ", id:",plat_id)
    page_max=getPages(plat_id)
    #page_max=2
    print("Pages:",page_max)
    for page_num in range(1,(page_max + 1)):
        print("Processing page:",page_num)
        table=getTable(plat_id,page_num)
        table_rows=table.findAll('tr')
        for rownum, row in enumerate(table_rows):
            if int(page_num) > 1 and rownum == 0:
                pass
            else:
                all_rows.append(row)

    new_table=[]

    header_row=getHeader(all_rows[0])
    new_table.append(header_row)

    for row in all_rows[1:]:
        new_table.append(getRow(row))
    
    with open(platform_name + '.csv', 'w') as f:
        print("Writing",platform_name + '.csv')
        csv_file = csv.writer(f)
        csv_file.writerows(new_table)


#print(getTable('1','1'))


# get last page
#split_raw_pages=pages_raw.split('</a>')
#last_page_num=int(split_raw_pages[len(split_raw_pages) - 3]).split('>')[1])



