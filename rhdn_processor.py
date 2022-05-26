#!/usr/bin/env python3

import sys
from ragu_file import readCsvtoDicts,writeDictstoCsv


def processMode(input_dicts,process_file):
    output_list=[]
    process_dicts=readCsvtoDicts(process_file,"\t")
    for row in input_dicts:
        getcol=""
        for proc_row in process_dicts:
            if (row['hack_title'] == proc_row['Title']) and (row['author'] == proc_row['Released By']) and \
                (row['platform'] == "NES") and (row['original_title'] == proc_row['Original Game']) and \
                (row['release_date'] == proc_row['Date']):
                    getcol=proc_row['Get?']
                    break
        row['get_status'] = getcol
        output_list.append(row)
    return(output_list)


def main(args):
    mode="process"
    if (len(args) == 0) or (not type(args[0]) == str) or (len(args[0]) == 0):
        raise(FileNotFoundError,"No file defined")
    elif (len(args) == 1) or (not type(args[1]) == str) or (len(args[1]) == 0):
        mode="update"
    else:
        process_file=args[1]
    input_file=args[0]
    input_filename=input_file.split('.')
    output_file=input_filename[0]+'_processed.'+input_filename[1]


    input_dicts=readCsvtoDicts(input_file,"\t")
    
    if mode == "process":
        output_list=processMode(input_dicts,process_file)

    writeDictstoCsv(output_list,output_file,',',True)
        
                    






if __name__ == "__main__":
    main(sys.argv[1:])
