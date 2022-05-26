#!/usr/bin/env python3

import sys,os,getopt,re,shutil,binascii

def usage():
    print('cd_rommer.py -i <inputfile>')


def getBytes(inputfile,seek,amount):
    #seek=int(seek,16)
    with open(inputfile, "rb") as f:
        f.seek(seek,0)
        bytes=f.read(amount)
        return(bytearray(bytes))


def mergeBin(input_bytearray):
    byte_string=b''.join((binascii.unhexlify(i) for i in input_bytearray))
    return(byte_string)


start=0

def main(argv):
    global input_file
    input_file=''
    try:
        opts, args = getopt.getopt(argv,"hi:",["ifile="]) #,"ofile="])
    except getopt.GetoptError:
        usage
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            usage
            sys.exit()
        elif opt in ("-i", "--ifile"):
            input_file = arg
#        elif opt in ("-o", "--ofile"):
#            outputfile = arg


    try:
        bin_size=os.path.getsize(input_file)
    except Exception as err:
        raise Exception("Error getting file size: ",err)

    pos=0
    sector_size=2352
    sector_list=[]
    while pos <= 1:
        sector={}
        sector_bytes=(getBytes(input_file, pos, sector_size))
        print(len(sector_bytes) / 98)
        pos+=sector_size
        sector["header"]=sector_bytes[:16]
        mode=sector["header"][15]
        if mode == 1:
            sector["data"]=sector_bytes[16:2064]
            sector["EDC"]=sector_bytes[2064:2068]
            sector["ECCP"]=sector_bytes[2076:2248]
            sector["ECCQ"]=sector_bytes[2248:2352]




        


            
            



    #print(sector_list[0])


if __name__ == "__main__":
   main(sys.argv[1:])