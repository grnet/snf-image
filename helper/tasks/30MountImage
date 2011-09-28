#! /bin/bash

### BEGIN TASK INFO
# Provides:		MountImage
# RunBefore:		UmountImage
# Short-Description:	Mount the partition that hosts the image
### END TAST INFO

set -e
. /usr/share/snf-image/common.sh

if [ -z "$SNF_IMAGE_TARGET" ]; then
    log_error "Target dir:\`$SNF_IMAGE_TARGET\' is missing"
fi

if [ ! -b "$SNF_IMAGE_DEV"]; then
    log_error "Device file:\`$SNF_IMAGE_DEV\' is not a block device"
fi

mount $SNF_IMAGE_DEV $SNF_IMAGE_TARGET

exit 0
# vim: set sta sts=4 shiftwidth=4 sw=4 et ai :
