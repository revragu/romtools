#!/bin/bash

sourcedir="$1"

find "$sourcedir" -type f -regextype posix-extended -regex "^.*\.(zip|7z|rar)$" | while read -r zipfile; do
    dir=$(echo "$zipfile" | sed -E 's/(^.*)\/.*/\1/')
    7za e -y -o"$dir" "$zipfile"
done