# Copyright (C) 2011 GRNET S.A. 
# Copyright (C) 2007, 2008, 2009 Google Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.

RESULT=/dev/ttyS1
FLOPPY_DEV=/dev/fd0
PROGNAME=$(basename $0)

PATH=/sbin:/bin:/usr/sbin:/usr/bin:/usr/local/sbin:/usr/local/bin

# Programs
XMLSTARLET=xmlstarlet
E2FSCK=e2fsck
RESIZE2FS=resize2fs
PARTED=parted
REGLOOKUP=reglookup
CHNTPW=chntpw

CLEANUP=( )

add_cleanup() {
    local cmd=""
    for arg; do cmd+=$(printf "%q " "$arg"); done
    CLEANUP+=("$cmd")
}

log_error() {
    echo "ERROR: $@" | tee $RESULT >&2
    exit 1
}

warn() {
    echo "Warning: $@" >&2
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
            ID=$(grep ^DISTRIB_ID= ${root_dir}/etc/lsb-release | cut -d= -f2)
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

get_last_partition() {
    local dev="$1"

    "$PARTED" -s -m "$dev" unit s print | tail -1
}

get_partition() {
    local dev="$1"
    local id="$2"

    "$PARTED" -s -m "$dev" unit s print | grep "^$id" 
}

get_partition_count() {
    local dev="$1"

     expr $("$PARTED" -s -m "$dev" unit s print | wc -l) - 2
}

get_last_free_sector() {
    local dev="$1"
    local last_line=$("$PARTED" -s -m "$dev" unit s print free | tail -1)
    local type=$(echo "$last_line" | cut -d: -f 5)

    if [ "$type" = "free;" ]; then
        echo "$last_line" | cut -d: -f 3
    fi
}

cleanup() {
    # if something fails here, it shouldn't call cleanup again...
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
            # a `device-mapper: remove ioctl failed: Device or resource busy'
            # error. A sensible workaround for this is to wait for a while and
            # then try again.
            local cmd=${CLEANUP[$i]}
            $cmd || for interval in 0.25 0.5 1 2 4; do
            echo "Command $cmd failed!"
            echo "I'll wait for $interval secs and will retry..."
            sleep $interval
            $cmd && break
        done
	if [ "$?" != "0" ]; then
            echo "Giving Up..."
            exit 1;
        fi
    done
  fi
}


check_if_excluded() {

    test "$PROGNAME" = "snf-image-helper" && return 0

    eval local do_exclude=\$SNF_IMAGE_PROPERTY_EXCLUDE_${PROGNAME:2}_TASK
    if [ -n "$do_exclude" ]; then
        warn "Task $PROGNAME was excluded and will not run."
        exit 0
    fi

    return 0
}

trap cleanup EXIT

# Check if the execution of a task should be ommited
check_if_excluded

# vim: set sta sts=4 shiftwidth=4 sw=4 et ai :
