#!/usr/bin/env python3

import sys, http.client, re, time
# all my stuff for use in multiple scripts

def removeBlankLines(input_list):
    new_list = []
    strip_list = stripLTSpaces(input_list)
    for item in input_list:
        if item != '':
            new_list.append(item)
        else:
            pass
    return new_list



# strips leading and trailing spaces on all items in a list
def stripLTSpaces(input_list):
    new_list = []
    for item in input_list:
        new_list.append(item)

    for idx, item in enumerate(input_list):
        new_item = item.strip()
        new_list[idx] = new_item
        
    return new_list

def reverseString(input_string):
    
    char_list = []
    rev_string = ""
    for char in input_string:
        char_list.append(char)
    char_list.reverse()
    

    for char in char_list:
        rev_string = rev_string + char

    return rev_string


# os independent line splitter, basically so my unix stuff is parsed properly
def splitNewline(input_string):
    
    no_r = input_string.replace("\r\n","\n")
   
    if re.match(r'^\n+',no_r):
        no_r = re.sub(r'^\n+','',no_r)
    
    rev_no_r = reverseString(no_r)

    if re.match(r'^\n', rev_no_r):
        rev_no_r = re.sub(r'^\n+','\n',rev_no_r)

    no_r = reverseString(rev_no_r)

    split_content = no_r.split("\n")
    
    return split_content


# takes a list that's been split on a character and reconstitutes the escapes so that escaped characters stay put and don't create a separate list entry
def escapeList(input_list, escaped):
    # if input is not a list, split it at escaped
    is_list = isinstance(input_list, list)
    split_list = []
    if is_list == True:
        for item in input_list:
            split_list.append(item)
    else:
        split_list = input_list.split(escaped)

    new_list = []
    matched_string = ''
    for string in split_list:
        # for some reason this doesn't want to match strings with \\$ until the last iteration, so we reverse to match on ^\\
        reverse_string = string[::-1]
        
        if re.match(r'^\\', reverse_string):
            matched_string = matched_string + string + escaped
        elif matched_string != '':
            matched_string = matched_string + string
            new_list.append(matched_string)
            matched_string = ''
        else:
            
            new_list.append(string)
    
    return new_list

# returns true if value is integer
def isInteger(n):
    try:
        float(n)
    except ValueError:
        return False
    else:
        return float(n).is_integer()


# takes a list of dicts, and the fields (keys) for those dicts
# for matching fields in each dict, convert value to integer 
def integerizeFields(input_list,input_fields):
    output_list = []
    for item in input_list:
        output_list.append(item)
        
    for field in input_fields:
        for idx, item in enumerate(input_list):
            try:
                output_list[idx][field] = int(item[field])
            except ValueError as e:
                raise ValueError("can't convert " + output_list[idx][field] + " to integer in field " + field + ", dict: " + str(item))
    return output_list


# takes a list of indices and a list
# deletes all items on list at indices
# reverses indices list so that the list indexes changing as items are deleting will not cause the wrong list items to be deleted, since it will be deleting the highest indexed entries first
def delIndiceList(indice_list,input_list):
    indice_list.sort()
    indice_list.reverse()
    output_list = []
    for item in input_list:
        output_list.append(item)
    
    for index in indice_list:
        del output_list[index]
        
    return output_list


# sort a list of dicts by a field in the dicts
def sortByField(unsorted_list, field):
    output_list = []
    field_items = []
    work_list = []

    for item in unsorted_list:
        work_list.append(item)
    
    for item in unsorted_list:
        field_value = item[field]
        field_items.append(field_value)
    
    # remove dupes
    field_items = list(dict.fromkeys(field_items))
    
    # sort field list
    field_is_integer = isInteger(field_items[0])
    if field_is_integer == True:
        sorted_field = sorted(field_items)
        sorted_field.reverse()
    else:
        sorted_field = sorted(field_items, key=str.casefold)    
    
    for field_value in sorted_field:
        indice_list = []
        for idx, item in enumerate(unsorted_list):
            if field_value == item[field]:
                output_list.append(item)
                indice_list.append(idx)
        
        work_list = delIndiceList(indice_list, work_list)
        unsorted_list.clear()
        for item in work_list:
            unsorted_list.append(item)
        
    return output_list

    
# from a list of dicts, get the keys for the first entry
# this is for generating a csv header
def getHeader(input_list):
    output_list = []
    header = []
    current_list = []
    for idx, current_dict in enumerate(input_list):
        
        if idx == 0:
            for k,v in current_dict.items():
                header.append(k)
        
        for k, v in current_dict.items():
            current_list.append(v)
        
        output_list.append(current_list)
        current_list = []
    
    return header, output_list

def main():
    pass


if __name__ == "__main__":
    main(sys.argv[1:])