#!/usr/bin/env python3

import sys,os,getopt,re,shutil

def getBytes(inputfile,seek,amount,return_range=False):
    range_loc=int(hex(0x7fff),16)
    seek=int(seek,16)
    with open(inputfile, "rb") as f:
        f.seek(seek,0)
        chksum_bytes=f.read(amount)
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

def getChecksum(inputfile):
    byte_array=bytearray(getBytes(inputfile,hex(0x200),-1))
    words=[]

    while len(byte_array) > 0:
        byte1=int.to_bytes(byte_array[0],1,'big')
        byte2=int.to_bytes(byte_array[1],1,'big')
        word=b''.join([byte1,byte2])
        del byte_array[0]
        del byte_array[0]
        words.append(word)

    sum=0
    for word in words:
        sum=int.from_bytes(word,'big')+sum

    checksum=sum % 65536
    checksum_bytes=checksum.to_bytes(2,'little')
    

    return(checksum_bytes)



def main(argv):
    global inputfile
    global outputfile
    inputfile=''
    outputfile=''
    try:
        opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
    except getopt.GetoptError:
        print('md_checksum_fixer.py -i <inputfile> -o <outputfile>')
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
        outputfile=re.sub(r'\.(md)$','_out.\\1',inputfile)

    print('Input:',inputfile)
    print('Output:',outputfile)
    rom_size=getSize(inputfile)
    header_checksum=getBytes(inputfile,hex(0x18E),2)
    print("Checksum in header:",hex(int.from_bytes(header_checksum,'big')))
    correct_checksum=getChecksum(inputfile)
    print("Correct checksum:",hex(int.from_bytes(correct_checksum,'little')) )

    writeBytes(inputfile,hex(0x18E),bytearray(correct_checksum),outputfile)


if __name__ == "__main__":
   main(sys.argv[1:])