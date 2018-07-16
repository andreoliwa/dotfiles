#!/bin/bash
label=$1
echo Mounting ${label} as read/write
sudo mkdir -p /Volumes/NTFS

device=$(diskutil list | rg ${label} | awk '{print $6}')
sudo ntfs-3g /dev/${device} /Volumes/NTFS -olocal -oallow_other
