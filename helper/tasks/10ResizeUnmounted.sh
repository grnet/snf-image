#! /bin/sh

### BEGIN TASK INFO
# Provides:		ResizeUnmounted
# RunBefore:		MountImage
# Short-Description:	Resize filesystem to use all the available space
### END TAST INFO

set -e
. /usr/share/snf-image/common.sh

if [ ! -b "$SNF_IMAGE_DEV" ]; then
    log_error "Device file:\`$SNF_IMAGE_DEV\' is not a block device"

fi
if [ -z "$SNF_IMAGE_TYPE" ]; then
    log_error "Image type does not exist"
fi

if [ "$SNF_IMAGE_TYPE" = "extdump" ]; then
    $RESIZE2FS $SNF_IMAGE_DEV
fi	

exit 0
# vim: set sta sts=4 shiftwidth=4 sw=4 et ai :
