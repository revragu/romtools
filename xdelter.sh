#!/bin/bash
input_dir="$1"
input_file="$2"
format="$3"

if [[ $format == "" ]]; then
    format="xdelta"
fi

input_filename="$(echo "$input_file" | rev | cut -d'/' -f1 | rev)"
input_ext="$(echo "$input_file" | rev | cut -d'.' -f1 | rev)"
input_filename_noext=$(echo "$input_filename" | sed -E "s/(.*)\.${input_ext}$/\1/")

find "$input_dir" -type f -name "*.${format}" | while read -r xdfile; do
    source_dir=$(echo "$xdfile" | sed -E 's/(^.*\/).*/\1/')
    xd_filename="$(echo "$xdfile" | sed -E 's/^.*\/(.*)\..*/\1/')"
    newfile="${source_dir}${input_filename_noext}-${xd_filename}.${input_ext}"
    echo "input file: $input_file"
    echo "input filename: $input_filename_noext"
    echo "input extension: $input_ext"
    echo "source dir: $source_dir"
    echo "patch filename: $xd_filename"
    echo "new filename: $newfile"
    if [[ $format == "xdelta" ]]; then
        xdelta3 -d -s "$input_file" "$xdfile" "$newfile"
    elif [[ $format == "bps" || $format == "ips" ]]; then
        flips -a "$xdfile" "$input_file" "$newfile"
    fi
done

exit 0