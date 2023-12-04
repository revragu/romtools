#!/usr/bin/env python3

import getopt, sys, os, multiprocessing
from operator import itemgetter
from nes_reader import nesinfo
from ragu_file import writeJson



def usage():
    pass

# try and except to return 0 if a key value pair doesn't exist
def ifExists(input_dict, val):
    try:
        return(input_dict[val])
    except:
        return(0)

# return header configurations, stripped of prg-rom and chr-rom bytes
# count how many of each unique configuration there is, and collect checksums
# for all roms that use that config
def getConfs(roms):
    header_list=[]
    for n in range(0,len(roms)):
        # sanitize raw header
        header_array=bytearray(roms[n]["Raw Header"])
        header_array[4]=0;header_array[5]=0;header_array[9]=0
        header_bytes=bytes(header_array)
        roms[n]["Raw Header"]=str(header_bytes.hex())
        roms[n]["PRG Data"]={
            "data": (roms[n]["ROM Object"]).prgrom.data,
            "sha": (roms[n]["ROM Object"]).prgrom.hash('sha256'),
            "filename":(roms[n]["Input ROM"])
        }
    # sort and uniq each header
    unique_headers=sorted(
        set(
            [rom["Raw Header"] for rom in roms]
        )
    )

    all_headers=[]
    # next, count number of roms for each header, sort by number
    for header in unique_headers:
        header_roms=[rom for rom in roms if rom['Raw Header'] == header]
        headers_info={
            "count": len(header_roms),
            "header": header,
            "prg_data": [rom["PRG Data"] for rom in header_roms]
        }
        all_headers.append(headers_info)
    return(sorted(all_headers,key=itemgetter('count'),reverse=True))
        

# figure out if there is a default configuration for a mapper
def getDefault(confs):
    default_candidate=confs[0]
    num_of_defaults=1
    # mark all as not default
    if len(confs) > 1:
        num_of_defaults=len(\
            [conf["count"] for conf in confs if conf["count"] == \
                default_candidate["count"]])
    if num_of_defaults > 1:
        return(False)

    # don't need prg data for the default, just shas
    confs[0]["prg_data"]=""
    # mark as default
    confs[0]["default"]=True
    return(confs[0])
            

def makePrgs(conf):
    try:
        os.mkdir('mapperer_prg')
    except FileExistsError:
        pass
    except Exception as e:
        raise Exception("Can't create new mapperer_prg directory: ",e)
    
    
    for prg in conf["prg_data"]:
        with open('mapperer_prg/'+prg['sha'], 'wb') as binfile:
            binfile.write(prg["data"])
        
            


def compileConfs(confs):
    conf_list=[]
    for n,conf in enumerate(confs):
        if n == 0:
            # returns default configuration stripped of hashs
            # confs[0] should be the default since the list is sorted by count, 
            # but if it isn't, getDefault returns False
            default_conf=getDefault(confs)
            if default_conf != False:
                conf_list.append(default_conf)
                continue
        conf["default"]=False
        # make prgrom files for non-default roms
        makePrgs(conf)
        for m,prg in enumerate(conf["prg_data"]):
            prg.pop("data")
            conf["prg_data"][m] = prg
        
        conf_list.append(conf)
    return(conf_list)
    
def getRomInfo(file):
    return(nesinfo(file,True))

def mapperer(list_of_files,filename='mapper_confs.json'):
    mappers_list=[]
    # run getRomInfo to put info about all roms into list of dicts
    # multiprocessing makes it way faster
    cpus=multiprocessing.cpu_count()
    pool_obj = multiprocessing.Pool(processes=cpus) 
    rominfo_list = pool_obj.map(getRomInfo,list_of_files)
    # from the list we can determine all the mappers
    mappers=sorted(set(\
        [mapper_dict['Number'] for mapper_dict in\
        [rom['Mapper'] for rom in rominfo_list]]\
        ))
    for n in mappers:
        mapper_roms=[]
        
        mapper_roms=[rom for rom in rominfo_list\
            if rom['Mapper']['Number'] == n]
        confs=getConfs(mapper_roms)

        mappers_list.append({ "mapper" : n, "header_confs": compileConfs(confs)})
    
    writeJson(mappers_list,filename)
    
    

def main(argv):    
    try:
        opts, args = getopt.getopt(argv,"hd:",["directory="])
    except getopt.GetoptError:
        usage()
        raise(getopt.GetoptError("Invalid option",))
    for opt, arg in opts:
        if opt == '-h':
            usage()
            sys.exit()
        elif opt in ("-d", "--directory"):
            input_dir = arg
            list_of_files=[]
            try:
                for root, dirs, files in os.walk(input_dir):
                    for file in files:
                        if(file.endswith(".nes")):
                            list_of_files.append(os.path.join(root,file))
            except FileNotFoundError:
                raise FileNotFoundError("Input dir "+input_dir+" not found")
            except PermissionError:
                raise PermissionError(\
                    "Unable to read input dir "+input_dir+\
                        " due to permissions restrictions")
            except Exception as e:
                raise Exception("Unknown error opening input dir "+input_dir+": "+e)

    
    mapperer(list_of_files)


    #print(rominfo_list)

    


if __name__ == "__main__":
    main(sys.argv[1:])