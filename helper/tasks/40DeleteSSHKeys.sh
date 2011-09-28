#! /bin/bash

### BEGIN TASK INFO
# Provides:		DeleteSSHKeys
# Requires:             MountImage
# Short-Description:	Remove ssh keys if present.
### END TAST INFO

set -e
. /usr/share/snf-image/common.sh


if [ "$SNF_IMAGE_TYPE" != "extdump" ]; then
    exit 0
fi

HOST_KEY="/etc/ssh/ssh_host_key"
RSA_KEY="/etc/ssh/ssh_host_rsa_key"
DSA_KEY="/etc/ssh/ssh_host_dsa_key"

for key in $HOST_KEY $RSA_KEY $DSA_KEY ; do
    if [ -f "${SNF_IMAGE_TARGET}/${key}" ] ; then
        rm -f ${SNF_IMAGE_TARGET}/${key}*
    fi
done

cleanup
trap - EXIT

exit 0

# vim: set sta sts=4 shiftwidth=4 sw=4 et ai :

