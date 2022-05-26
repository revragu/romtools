#!/bin/bash
src=$1
dest=$2


OLDIFS=$IFS
IFS=$'\t'
cat "$src" | while read -r sha title; do
	cat "$dest" | grep "$sha" | cut -d$'\t' -f2- | while read -r filename; do
		echo "$filename"
		rm -f "$filename"
	done
done
