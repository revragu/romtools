#!/bin/bash
src=$(realpath "$1")
dest=$(realpath "$2")

find "$src" -type f -exec sha1sum {} \; | sort -u -t' ' -k1,1 | sed -E 's/([a-z0-9]+)  (.*)/\1\t\2/' > sourcesha.txt 
find "$dest" -type f -exec sha1sum {} \; | sed -E 's/([a-z0-9]+)  (.*)/\1\t\2/' > destsha.txt

./deduper.sh "sourcesha.txt" "destsha.txt"
