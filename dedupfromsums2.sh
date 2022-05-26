#!/bin/bash
sums=$1
src=$2

cat "$1" | while read -r sum; do
	count=0
	grep "$sum" $2 | while read -r sum filename; do
		if [[ $count -eq 0 ]]; then
			echo "keep $filename"
		else
			rm -f "$filename"
		fi
		count+=1
	done
done
