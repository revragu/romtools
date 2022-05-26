#!/bin/bash

sourcedir="$1"
romdir="$2"

find "$sourcedir" -maxdepth 1 -type d  | while read -r dir; do
    dirname=$(echo "$dir" | sed -E 's/^.*\/(.*)/\1/' | tr "'" '*' | tr '.' '*')
    find "$romdir" -type f -iname "*${dirname}*" | while read -r rom; do
        cp "$rom" "$dir"
    done
done