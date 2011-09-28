#! /bin/bash

### BEGIN TASK INFO
# Provides:		InstallUnattend
# RunBefore:		UmountImage
# RunAfter:		MountImage
# Short-Description:	Installs Unattend.xml for unattended windows setup
### END TAST INFO

set -e
. /usr/share/snf-image/common.sh

if [ -z "$SNF_IMAGE_TARGET" ]; then
	log_error "Target dir is missing"	
fi

if [ "$SNF_IMAGE_TYPE" != "ntfsdump" ]; then
	exit 0
fi

if [ -e /usr/share/snf-image/unattend.xml ]; then
	cat /usr/share/snf-image/unattend.xml > $SNF_IMAGE_TARGET/Unattend.xml
fi

exit 0
