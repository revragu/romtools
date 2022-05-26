#!/usr/bin/env python3

import sys,os,getopt,re,shutil,binascii

def usage():
    print('data_getter.py -i <inputfile> -o <outputfile> -b 0x<start hex value> -e 0x<end hex value)')


def getBytes(inputfile,seek,amount):
    #seek=int(seek,16)
    with open(inputfile, "rb") as f:
        f.seek(int(seek),0)
        output_bytes=f.read(int(amount))
        return(output_bytes)

def outBytes(outputfile, input_bytes):
    print("outputting",outputfile)
    with open(outputfile, "wb") as file:
        file.write(input_bytes)

def fileTest(inputfile):
    try:
        with open(inputfile, "rb") as f:
            return(0)
    except:
        raise FileNotFoundError


def mergeBin(input_bytearray):
    byte_string=b''.join((binascii.unhexlify(i) for i in input_bytearray))
    return(byte_string)


start=0

def main(argv):
    input_file=None
    output_file=None
    start=None
    end=None
    try:
        opts, args = getopt.getopt(argv,"hi:o:s:e:",["ifile=","ofile=","start=","end="])
    except getopt.GetoptError:
        usage
        raise(getopt.GetoptError("Invalid option",))
    for opt, arg in opts:
        if opt == '-h':
            usage
            sys.exit()
        elif opt in ("-i", "--ifile"):
            input_file = arg
        elif opt in ("-o", "--ofile"):
            output_file = arg
        elif opt in ("-s", "--start"):
            start = arg
        elif opt in ("-e", "--end"):
            end = arg
    
    try:
        fileTest(input_file)
    except:
        usage
        raise FileNotFoundError("No input file defined")
    
    

    if output_file is None:
        if re.search(r'^.*\..*$', input_file):
            output_filename=os.path.dirname(os.path.realpath(input_file)) + '/' + \
                re.sub(r'^(.*)\.(.*)$',r'\1_out.\2',os.path.basename(input_file))
        else:
            output_filename=os.path.dirname(os.path.realpath(input_file)) + '/' + \
                os.path.basename(input_file) + '_out'
    
    input_size=int(os.path.getsize(input_file))
    if start is None:
        usage
        raise ValueError("Start address must be specified")
    else:
        try:
            start_loc=int(start,16)
        except:
            raise ValueError("Start address not valid hex address")
    
    if end is None:
        end_loc=input_size
    else:
        try:
            end_loc=int(end,16)
        except:
            raise ValueError("End address not valid hex address")
    
    if end_loc < start_loc:
        raise ValueError("End address is before start address")
    elif end_loc > input_size:
        raise ValueError("End address exceeds length of input file")

    amount=end_loc - start_loc
    extract_bytes=getBytes(input_file, start_loc, amount)

    outBytes(output_filename, extract_bytes)


    #print(sector_list[0])


if __name__ == "__main__":
   main(sys.argv[1:])