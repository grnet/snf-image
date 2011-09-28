# Copyright 2011 GRNET S.A. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#   1. Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#
#  2. Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
#
# The views and conclusions contained in the software and documentation are
# those of the authors and should not be interpreted as representing official
# policies, either expressed or implied, of GRNET S.A.

OUTPUT=/dev/ttyS0
RESULT=/dev/ttyS2
FLOPPY_DEV=/dev/fd0

# Programs
XMLSTARLET=xmlstarlet
RESIZE2FS=resize2fs

CLEANUP=( )

log_error() {
    echo "$@" >&2
    exit 1
}

get_base_distro() {
    local root_dir=$1

    if [ -e "$root_dir/etc/debian_version" ]; then
        echo "debian"
    elif [ -e "$root_dir/etc/redhat-release" ]; then
        echo "redhat"
    elif [ -e "$root_dir/etc/slackware-version" ]; then
        echo "slackware"
    elif [ -e "$root_dir/SuSE-release" ]; then
        echo "suse"
    elif [ -e "$root_dir/gentoo-release" ]; then
        echo "gentoo"
    fi
}

get_distro() {
    local root_dir=$1

    if [ -e "$root_dir/etc/debian_version" ]; then
        distro="debian"
        if [ -e ${root_dir}/etc/lsb-release ]; then
            ID=$(grep $DISTRIB_ID=${root_dir}/etc/lsb-release | cut -d= -f2)
            if [ "x$ID" = "xUbuntu" ]; then
                distro="ubuntu"
            fi
        fi
        echo "$distro"
    elif [ -e "$root_dir/etc/fedora-release" ]; then
        echo "fedora"
    elif [ -e "$root_dir/etc/centos-release" ]; then
        echo "centos"
    elif [ -e "$root_dir/etc/redhat-release" ]; then
        echo "redhat"
    elif [ -e "$root_dir/etc/slackware-version" ]; then
        echo "slackware"
    elif [ -e "$root_dir/SuSE-release" ]; then
        echo "suse"
    elif [ -e "$root_dir/gentoo-release" ]; then
        echo "gentoo"
    fi
}

cleanup() {
# if something fails here, it souldn't call cleanup again...
    trap - EXIT

    if [ ${#CLEANUP[*]} -gt 0 ]; then
        LAST_ELEMENT=$((${#CLEANUP[*]}-1))
        REVERSE_INDEXES=$(seq ${LAST_ELEMENT} -1 0)
        for i in $REVERSE_INDEXES; do
            # If something fails here, it's better to retry it for a few times
            # before we give up with an error. This is needed for kpartx when
            # dealing with ntfs partitions mounted through fuse. umount is not
            # synchronous and may return while the partition is still busy. A
            # premature attempt to delete partition mappings through kpartx on a
            # device that hosts previously mounted ntfs partition may fail with
            # an  `device-mapper: remove ioctl failed: Device or resource busy'
            # error. A sensible workaround for this is to wait for a while and
            # then try again.
            local cmd=${CLEANUP[$i]}
            $cmd || for interval in 0.25 0.5 1 2 4; do
            echo "Command $cmd failed!"
            echo "I'll wait for $interval secs and will retry..."
            sleep $interval
            $cmd && break
        done
        test $? -eq 1 && { echo "Giving Up..."; exit 1; }
    done
  fi
  echo "Clean UP executed"
}

trap cleanup EXIT

# Redirect stdout and stderr
exec &> $OUTPUT

# vim: set sta sts=4 shiftwidth=4 sw=4 et ai :
