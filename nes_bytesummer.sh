#!/bin/bash

source="$1"
dest_dir="$2"

function bytesum(){
    source=$1
    rom=$2
    ./nes_reader.py -i "$source" | jq '."ROMS"' | jq '.["'"${rom}"'"]' | jq '."Bytesum"'
    exitcode=$?
    if [[ $exitcode > 0 ]]; then
        exit 1
    else
        exit 0
    fi
}

name=$(echo "$source" | sed -E 's/^.*\/(.*)/\1/')
prgrom=$(bytesum "$source" "PRG-ROM")
chrrom=$(bytesum "$source" "CHR-ROM") 2>/dev/null
exitcode=$?
if [[ $exitcode > 0 ]]; then
    chrrom=0
fi
    
find "$dest_dir" -type f -name "*.nes" | while read -r rompath; do
    chrper=0
    newprg=$(bytesum "$rompath" "PRG-ROM")
    newchr=$(bytesum "$rompath" "CHR-ROM")
    exitcode=$?
    if [[ $exitcode -ge 1 ]]; then
        newchr=0
    fi  

    prgdiff=$(echo "$(( newprg - prgrom ))" | sed "s/^-//" )
    prgper=$(echo "scale=2;100*($prgdiff / $prgrom)" | bc -l )
    if [[ $chrrom -gt 0 ]] && [[ $newchr -gt 0 ]]; then
        chrdiff=$(echo "$(( newchr - chrrom ))" | sed "s/^-//" )
    elif ([[ $chrrom -gt 0 ]] && [[ $newchr -le 0 ]]) || ([[ $chrrom -le 0 ]] && [[ $newchr -gt 0 ]]); then
        chrper=100
    else
        chrper="NA"
    fi
    
    if [[ $chrper == 0 ]]; then
        chrper=$(echo "scale=2;100*($chrdiff / $chrrom)" | bc -l )
    fi
    if [[ $chrper != "NA" ]]; then
        avgper=$(echo "scale=2;100*(($prgper+$chrper)/200)" | bc -l)
    else
        avgper=$prgper
    fi


    echo "$rompath PRG ${prgper}% CHR ${chrper}% AVG ${avgper}" | sed -E 's/^.*\/(.*)/\1/'
done