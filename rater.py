#!/usr/bin/env python3

from ragu_file import readCsv,writeCsv

FILE="Nintendo_Entertainment_System.csv"

csv_file=readCsv(FILE)

new_table=[]
header=[]
for i in csv_file[0]:
    header.append(i)

header.append('BinMods')

for line in csv_file:
    line['Mods']=line['Mods'].replace(' ','')
    line['Mods']=line['Mods'].replace('GP','16')
    line['Mods']=line['Mods'].replace('G','1')
    line['Mods']=line['Mods'].replace('L','2')
    line['Mods']=line['Mods'].replace('T','4')
    line['Mods']=line['Mods'].replace('S','8')
    line['Mods']=line['Mods'].replace('O','32')
    mods=line['Mods'].split(',')
    line['BinMods']=int(0)
    try:
        for mod in mods:
            line['BinMods']=int(line['BinMods']) + int(mod)
    except:
        line['BinMods']=mods

    new_table.append(line)

    new_csv=[]

for line in new_table:
    new_line=[]
    for k,v in line.items():
        new_line.append(v)
        
    new_csv.append(new_line)

print(new_csv)


writeCsv(FILE+'_new.csv',header,new_csv)