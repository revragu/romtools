#!/bin/bash
sourcedir="$1"
destext="$2"

find "$sourcedir" -mindepth 1 -maxdepth 1 -type d | while read -r gamedir; do
    
    find "$gamedir" -type f -regextype posix-extended -regex ".*\.((i|I|b|B)(p|P)(s|S))" | while read -r ipsfile; do
        
        patchname=$(echo "$ipsfile" | sed -E 's/.*\/(.*)\..*/\1/')
        find "$gamedir" -type f -iname "*.${destext}" | while read -r romfile; do
            romname=$(echo "$romfile" | sed -E 's/.*\/(.*)\..*/\1/')
            echo "current dir: $gamedir"
            echo "src ips: $patchname"
            echo "src rom: $romname"
            echo "dest rom: ${gamedir}/${romname}-${patchname}.${destext}"
            flips -a "$ipsfile" "$romfile" "${gamedir}/${romname}-${patchname}.${destext}"
        done
    done
done
