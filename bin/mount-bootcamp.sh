#!/usr/bin/env bash
# Mount the Bootcamp volume on macOS

if [ "$(uname -s)" != "Darwin" ]; then
    echo "This script is only for macOS"
    exit 1
fi

BOOTCAMP_DISK_DEVICE=$(diskutil list | rg -e bootcamp -e osxfuse \
    | rg -o disk.+)
echo "Bootcamp disk: $BOOTCAMP_DISK_DEVICE"
sudo umount /dev/$BOOTCAMP_DISK_DEVICE

# Delete empty volumes
sudo find /Volumes -mindepth 1 -maxdepth 1 -empty -print -delete

sudo /usr/local/bin/ntfs-3g /dev/$BOOTCAMP_DISK_DEVICE \
    /Volumes/WinHD -olocal -oallow_other

ls -l /Volumes
set -x
ls -l /Volumes/WinHD
