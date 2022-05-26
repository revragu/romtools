#!/bin/bash

sourcedir=$1
romext=$2

find "$sourcedir"  -mindepth 1 -maxdepth 1 -type d | while read -r dir; do
  romarray=()
  patcharray=()
  while IFS= read -r -d $'\0'; do
    romarray+=("${REPLY}")
  done < <(find "${dir}" -type f -iregex "^.*\.${romext}$" -print0)
  while IFS= read -r -d $'\0'; do
    patcharray+=("${REPLY}")
  done < <(find "${dir}" -type f -regextype posix-extended -iregex "^.*\.(ips|bps|xdelta)$" -print0)
  #done < <(find "${dir}" -type f -regextype posix-extended -iregex "^.*\.xdelta$" -print0)
  patchcount=$(printf "%s\n" "${patcharray[@]}" | wc -l)


  for rom in "${romarray[@]}"; do
    romfile=$(echo "$rom" | sed -E "s/^.*\/(.*)$/\1/")
    romdir=$(echo "$rom" | sed -E "s/^(.*\/).*$/\1/")
    romname=$(echo $romfile | sed -E "s/^(.*)\..*/\1/")
    for patch in "${patcharray[@]}"; do
      patchpath=$(echo ${patch//"$dir"/""} | sed -E "s/^\///")
      patchdirs=$(echo "$patchpath" | sed -E "s/^(.*)\/.*$/\1/")
      patchfullname=$(echo "$patchpath" | sed -E "s/^.*\/(.*)$/\1/")
      patchname=$(echo "$patchfullname" | sed -E "s/^(.*)\..*$/\1/")
      patchext=$(echo "$patchfullname" | sed -E "s/^.*\.(.*)$/\1/" | tr 'A-Z' 'a-z')
      if [[ $patchcount -eq 1 ]]; then
        output_name="$romname (${patchdirs//"/"/""}).$romext"
      else
        output_name="$romname (${patchdirs//"/"/""} $patchname).$romext"
      fi
      if [[ "$patchext" == "ips" || "$patchext" == "bps" ]]; then
        flips -a "$patch" "$rom" "${dir}/${output_name}"
      elif [[ "$patchext" == "xdelta" ]]; then
        xdelta3 -d -s "$rom" "$patch" "${dir}/${output_name}"
      fi
      #echo "$patchpath"
      #echo "$patchdirs"
      #echo "$patchname"
    done

  done


done