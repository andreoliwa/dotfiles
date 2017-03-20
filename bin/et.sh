#!/bin/bash
# Exif Tool script to handle images
V_DIR=$1
if [[ "$V_DIR" == '' ]]; then
  echo Supply a directory.
  exit
fi

V_DIR_FORMAT=year/%Y/%m-%B_%d-%A

rmdir-empty.sh
exiftool '-Directory<CreateDate' -if '$CreateDate' -d $V_DIR_FORMAT -r $V_DIR
exiftool '-Directory<ModifyDate' -if '$ModifyDate' -d $V_DIR_FORMAT -r $V_DIR
# exiftool '-*Date*' --FileAccessDate --FileInodeChangeDate -s -if 'not $CreateDate' -r $V_DIR
rmdir-empty.sh
