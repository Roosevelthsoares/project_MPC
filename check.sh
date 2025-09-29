#!/usr/bin/env bash

DIR="$1"
EXT="$2"

if [[ -z "$DIR" || -z "$EXT" ]]; then
  echo "Usage: $0 <directory> <extension>"
  exit 1
fi

if [[ ! -d "$DIR" ]]; then
  echo "Error: Directory $DIR does not exist."
  exit 1
fi

all_good=true

for file in "$DIR"/*; do
[[ -f "$file" ]] || continue

  if [[ "$file" != *.$EXT ]]; then
    echo "File $file does not have the expected .$EXT extension."
    all_good=false
  fi
done

if $all_good; then
  echo "All files in $DIR have the .$EXT extension."
  exit 0
else
  echo "Some files in $DIR do not have the .$EXT extension."
  exit 1
fi