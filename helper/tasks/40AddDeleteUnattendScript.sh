#! /bin/bash

### BEGIN TASK INFO
# Provides:		AddDeleteUnattendScript
# RunBefore:		UmountImage
# RunAfter:		MountImage
# Short-Description:	Script that removes Unattend.xml after setup has finished
### END TAST INFO

set -e
. /usr/share/snf-image/common.sh

if [ -z "$SNF_IMAGE_TARGET" ]; then
	log_error "Target dir is missing"	
fi

if [ "$SNF_IMAGE_TYPE" != "ntfsdump" ]; then
	exit 0
fi

# Make sure Unattend.xml is removed after setup has finished
mkdir -p "$SNF_IMAGE_TARGET/Windows/Setup/Scripts"
echo "del /Q /F C:\Unattend.xml" > "$SNF_IMAGE_TARGET/Windows/Setup/Scripts/SetupComplete.cmd"

exit 0

# vim: set sta sts=4 shiftwidth=4 sw=4 et ai :

