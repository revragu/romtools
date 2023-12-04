#!/bin/bash

rom_path=$*

echo -e "file\tmapper" > nes10_mapper.tsv

find "$rom_path" -type f -name "*.nes" | while read -r nesrom; do
  format=$(./nes_reader.py -i "$nesrom" | jq '."Header Format"')
  mapper=$(./nes_reader.py -i "$nesrom" | jq '."Mapper"')
  if [[ "$format" == '"iNES"' ]]; then
    echo -e "${nesrom}\t${mapper}" >> nes10_mapper.tsv
  else
    rm -f "$nesrom" 
  fi
  
done
