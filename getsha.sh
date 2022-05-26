#!/bin/bash

while read -r file; do
	chksum=$(sha256sum "$file" | cut -d' ' -f1)
	echo -e "\"$file\"\t$chksum" 
done
