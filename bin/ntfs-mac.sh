#!/bin/bash
# Mount an NTFS external hard drive as read/write on macOS
LABEL=$1
DEVICE=$2
if [ -z "$LABEL" ]; then
    echo Missing external disk label.
    exit 1
fi

DIR=/Volumes/NTFS/${LABEL}
echo "Mounting $LABEL as read/write on $DIR"

test -z "$DEVICE" && DEVICE=$(diskutil list | rg ${LABEL} | rg -o disk.+)
if [ -z "$DEVICE" ]; then
    echo "Device empty, maybe the label does not exist; check below"
    diskutil list
    exit 2
fi

sudo mkdir -p $DIR
sudo ntfs-3g /dev/${DEVICE} $DIR -olocal -oallow_other
ls -l $DIR
open $DIR
