#!/usr/bin/env python3

import sys,os,getopt,re,shutil

def getBytes(inputfile,seek,amount,return_range=False):
    range_loc=int(hex(0x7fff),16)
    
    with open(inputfile, "rb") as f:
        f.seek(seek,0)
        chksum_bytes=f.read(amount)
        
        f.seek(range_loc,0)
        range=(int.from_bytes(f.read(1),'big') & 15)
        if return_range == True:
            return(chksum_bytes,range)
        else:
            return(chksum_bytes)


def writeBytes(inputfile,location_hex,bytes,outputfile):
    with open(inputfile,"rb") as f:
        buffer=bytearray(f.read(-1))

    location=int(location_hex,16) + 1

    for byte in bytes:
        buffer[location]=byte
        location-=1

    with open(outputfile,"wb") as f:
        f.write(buffer)

def getSize(filename):
    size=(os.path.getsize(filename)) / 1024
    return(int(size))

def getRanges(range_val):
    if range_val == 10:
        return([[0,int(hex(0x1ff0),16)]])
    elif range_val == 11:
        return([[0,int(hex(0x3ff0),16)]])
    elif range_val == 12:
        return([[0,int(hex(0x7ff0),16)]])
    elif range_val == 13:
        return([[0,int(hex(0xbff0),16)]])
    elif range_val == 14:
        return([[0,int(hex(0x7ff0),16)],[int(hex(0x8000),16),int(hex(0x10000),16)]])
    elif range_val == 15:
        return([[0,int(hex(0x7ff0),16)],[int(hex(0x8000),16),int(hex(0x20000),16)]])
    elif range_val == 0:
        return([[0,int(hex(0x7ff0),16)],[int(hex(0x8000),16),int(hex(0x40000),16)]])
    elif range_val == 1:
        return([[0,int(hex(0x7ff0),16)],[int(hex(0x8000),16),int(hex(0x80000),16)]])
    elif range_val == 2:
        return([[0,int(hex(0x7ff0),16)],[int(hex(0x8000),16),int(hex(0x100000),16)]])

    # if rom_size in (8,16,32,48):
    #     return([[0,((rom_size * 1024) - 16)]])
    # elif rom_size in (64,128,256,512,1024):
    #     return([[0,32752],[32768,(rom_size * 1024)]])
    # else:
    #     raise Exception("Invalid ROM size")

def getChecksum(inputfile,ranges,header_checksum,rom_size):
    bytes=bytearray()
    for range in ranges:
        amount=range[1] - range[0]
        currpage=bytearray(getBytes(inputfile,range[0],amount))
        
        bytes+=currpage        
    
    sum=0
    for byte in bytes:
        sum=byte+sum

    #if rom_size == 48:
    #    for byte in bytearray(header_checksum):
    #        sum=sum - byte
    #print(sum)

    checksum=sum % 65536        
    checksum_bytes=checksum.to_bytes(2,'big')

    #if rom_size == 48:
    #    for byte in bytearray(checksum_bytes):
    #        sum=sum - byte
    #print(sum)

    

    return(checksum_bytes)



def main(argv):
    global inputfile
    global outputfile
    inputfile=''
    outputfile=''
    try:
        opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
    except getopt.GetoptError:
        print('sms_checksum_fixer.py -i <inputfile> -o <outputfile>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('sms_checksum_fixer.py -i <inputfile> -o <outputfile>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg

    if inputfile == '':
        print('sms_checksum_fixer.py -i <inputfile> -o <outputfile>')
        raise Exception("No input file defined")

    if outputfile == '':
        outputfile=re.sub(r'\.(sms|gg)$','_out.\\1',inputfile)

    print('Input:',inputfile)
    print('Output:',outputfile)
    rom_size=getSize(inputfile)
    header_checksum,range=getBytes(inputfile,32762,2,True)
    print("Checksum in header:",hex(int.from_bytes(header_checksum,'big')))
    ranges=getRanges(range)
    correct_checksum=getChecksum(inputfile,ranges,header_checksum,rom_size)
    print("Correct checksum:",hex(int.from_bytes(correct_checksum,'big')) )

    writeBytes(inputfile,hex(0x7ffa),bytearray(correct_checksum),outputfile)


if __name__ == "__main__":
   main(sys.argv[1:])