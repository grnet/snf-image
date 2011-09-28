#! /bin/bash

### BEGIN TASK INFO
# Provides:		UmountImage
# RunBefore:
# RunAfter:		MountImage
# Short-Description:	Umount the partition that hosts the image
### END TAST INFO

set -e
. /usr/share/snf-image/common.sh

if [ -z "$SNF_IMAGE_TARGET" ]; then
	log_error "Target dir:\`$SNF_IMAGE_TARGET\' is missing"
fi

umount $SNF_IMAGE_TARGET

exit 0
