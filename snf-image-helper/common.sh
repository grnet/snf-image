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
MONITOR=/dev/ttyS2

FLOPPY_DEV=/dev/fd0
PROGNAME=$(basename $0)

PATH=/sbin:/bin:/usr/sbin:/usr/bin:/usr/local/sbin:/usr/local/bin

# Programs
XMLSTARLET=xmlstarlet
TUNE2FS=tune2fs
RESIZE2FS=resize2fs
PARTED=parted
SFDISK=sfdisk
MKSWAP=mkswap
BLKID=blkid
BLOCKDEV=blockdev
REGLOOKUP=reglookup
CHNTPW=chntpw

CLEANUP=( )
ERRORS=( )
WARNINGS=( )

add_cleanup() {
    local cmd=""
    for arg; do cmd+=$(printf "%q " "$arg"); done
    CLEANUP+=("$cmd")
}

log_error() {
    ERRORS+=("$@")
    echo "ERROR: $@" | tee $RESULT >&2
    exit 1
}

warn() {
    WARNINGS+=("$@")
    echo "Warning: $@" >&2
}

report_start_task() {

    local type="start-task"
    local timestamp=$(date +%s.%N)
    local name="${PROGNAME}"

    report+="\"type\":\"$type\","
    report+="\"timestamp\":$(date +%s.%N),"
    report+="\"name\":\"$name\"}"

    echo "$report" > "$MONITOR"
}

json_list() {
    declare -a items=("${!1}")
    report="["
    for item in "${items[@]}"; do
        report+="\"$(sed 's/"/\\"/g' <<< "$item")\","
    done
    if [ ${#report} -gt 1 ]; then
        # remove last comma(,)
        report="${report%?}"
    fi
    report+="]"

    echo "$report"
}

report_end_task() {

    local type="end-task"
    local timestam=$(date +%s.%N)
    local name=${PROGNAME}
    local warnings=$(json_list WARNINGS[@])

    report="\"type\":\"$type\","
    report+="\"timestamp\":$(date +%s),"
    report+="\"name\":\"$name\","
    report+="\"warnings\":\"$warnings\"}"

    echo "$report" > "$MONITOR"
}

report_error() {
    local type="ganeti-error"
    local timestamp=$(date +%s.%N)
    local location="${PROGNAME}"
    local errors=$(json_list ERRORS[@])
    local warnings=$(json_list WARNINGS[@])
    local stderr="$(cat "$STDERR_FILE" | sed 's/"/\\"/g')"

    report="\"type\":\"$type\","
    report+="\"timestamp\":$(date +%s),"
    report+="\"location\":\"$location\","
    report+="\"errors\":$errors,"
    report+="\"warnings\":$warnings,"
    report+="\"stderr\":\"$stderr\"}"

    echo "$report" > "$MONITOR"
}

get_base_distro() {
    local root_dir=$1

    if [ -e "$root_dir/etc/debian_version" ]; then
        echo "debian"
    elif [ -e "$root_dir/etc/redhat-release" ]; then
        echo "redhat"
    elif [ -e "$root_dir/etc/slackware-version" ]; then
        echo "slackware"
    elif [ -e "$root_dir/etc/SuSE-release" ]; then
        echo "suse"
    elif [ -e "$root_dir/etc/gentoo-release" ]; then
        echo "gentoo"
    else
        warn "Unknown base distro."
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
    elif [ -e "$root_dir/etc/SuSE-release" ]; then
        echo "suse"
    elif [ -e "$root_dir/etc/gentoo-release" ]; then
        echo "gentoo"
    else
        warn "Unknown distro."
    fi
}


get_partition_table() {
    local dev="$1"
    # If the partition table is gpt then parted will raise an error if the
    # secondary gpt is not it the end of the disk, and a warning that has to
    # do with the "Last Usable LBA" entry in gpt.
    if ! output="$("$PARTED" -s -m "$dev" unit s print | grep -E -v "^(Warning|Error): ")"; then
        log_error "Unable to read partition table for device \`${dev}'"
    fi

    echo "$output"
}

get_partition_table_type() {
    local ptable="$1"

    local dev="$(sed -n 2p <<< "$ptable")"
    declare -a field
    IFS=':' read -ra field <<< "$dev"

    echo "${field[5]}"
}

get_partition_count() {
    local ptable="$1"

    expr $(echo "$ptable" | wc -l) - 2
}

get_partition_by_num() {
    local ptable="$1"
    local id="$2"

    grep "^$id:" <<< "$ptable"
}

get_last_partition() {
    local ptable="$1"

    echo "$ptable" | tail -1
}

is_extended_partition() {
    local dev="$1"
    local part_num="$2"

    id=$($SFDISK --print-id "$dev" "$part_num")
    if [ "$id" = "5" ]; then
        echo "yes"
    else
        echo "no"
    fi
}

get_extended_partition() {
    local ptable="$1"
    local dev="$(echo "$ptable" | sed -n 2p | cut -d':' -f1)"

    tail -n +3 <<< "$ptable" | while read line; do
        part_num=$(cut -d':' -f1 <<< "$line")
        if [ $(is_extended_partition "$dev" "$part_num") == "yes" ]; then
            echo "$line"
            return 0
        fi
    done
    echo ""
}

get_logical_partitions() {
    local ptable="$1"

    tail -n +3 <<< "$ptable" | while read line; do
        part_num=$(cut -d':' -f1 <<< "$line")
        if [ $part_num -ge 5 ]; then
            echo "$line"
        fi
    done

    return 0
}

get_last_primary_partition() {
    local ptable="$1"
    local dev=$(echo "ptable" | sed -n 2p | cut -d':' -f1)

    for i in 4 3 2 1; do
        if output=$(grep "^$i:" <<< "$ptable"); then
            echo "$output"
            return 0
        fi
    done
    echo ""
}

get_partition_to_resize() {
    local dev="$1"

    table=$(get_partition_table "$dev")

    if [ $(get_partition_count "$table") -eq 0 ]; then
        return 0
    fi

    table_type=$(get_partition_table_type "$table")
    last_part=$(get_last_partition "$table")
    last_part_num=$(cut -d: -f1 <<< "$last_part")

    if [ "$table_type" == "msdos" -a $last_part_num -gt 4 ]; then
        extended=$(get_extended_partition "$table")
        last_primary=$(get_last_primary_partition "$table")
        ext_num=$(cut -d: -f1 <<< "$extended")
        prim_num=$(cut -d: -f1 <<< "$last_primary")

        if [ "$ext_num" != "$last_prim_num" ]; then
            echo "$last_prim_num"
        else
            echo "$last_part_num"
        fi
    else
        echo "$last_part_num"
    fi
}

create_partition() {
    local device="$1"
    local part="$2"
    local ptype="$3"

    declare -a fields
    IFS=":;" read -ra fields <<< "$part"
    local id="${fields[0]}"
    local start="${fields[1]}"
    local end="${fields[2]}"
    local size="${fields[3]}"
    local fs="${fields[4]}"
    local name="${fields[5]}"
    local flags="${fields[6]//,/ }"

    $PARTED -s -m -- $device mkpart "$ptype" $fs "$start" "$end"
    for flag in $flags; do
        $PARTED -s -m $device set "$id" "$flag" on
    done
}

enlarge_partition() {
    local device="$1"
    local part="$2"
    local ptype="$3"
    local new_end="$4"

    if [ -z "$new_end" ]; then
        new_end=$(cut -d: -f 3 <<< "$(get_last_free_sector "$device")")
    fi

    declare -a fields
    IFS=":;" read -ra fields <<< "$part"
    fields[2]="$new_end"

    local new_part=""
    for ((i = 0; i < ${#fields[*]}; i = i + 1)); do
        new_part="$new_part":"${fields[$i]}"
    done
    new_part=${new_part:1}

    # If this is an extended partition, removing it will also remove the
    # logical partitions it contains. We need to save them for later.
    if [ "$ptype" = "extended" ]; then
        local table="$(get_partition_table "$device")"
        local logical="$(get_logical_partitions "$table")"
    fi

    id=${fields[0]}
    $PARTED -s -m "$device" rm "$id"
    create_partition "$device" "$new_part" "$ptype"

    if [ "$ptype" = "extended" ]; then
        # Recreate logical partitions
        echo "$logical" | while read logical_part; do
            create_partition "$device" "$logical_part" "logical"
        done
    fi
}

get_last_free_sector() {
    local dev="$1"
    local unit="$2"

    if [ -n "$unit" ]; then
        unit="unit $unit"
    fi

    local last_line="$("$PARTED" -s -m "$dev" "$unit" print free | tail -1)"
    local ptype="$(cut -d: -f 5 <<< "$last_line")"

    if [ "$ptype" = "free;" ]; then
        echo "$last_line"
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
            # premature attempt to delete partition mappings through kpartx on
            # a device that hosts previously mounted ntfs partition may fail
            # with a `device-mapper: remove ioctl failed: Device or resource
            # busy' error. A sensible workaround for this is to wait for a
            # while and then try again.
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

task_cleanup() {
    rc=$?

    if [ $rc -eq 0 ]; then
       report_end_task
    else
       report_error
    fi

    cleanup
}

check_if_excluded() {

    local exclude=SNF_IMAGE_PROPERTY_EXCLUDE_TASK_${PROGNAME:2}
    if [ -n "${!exclude}" ]; then
        warn "Task $PROGNAME was excluded and will not run."
        exit 0
    fi

    return 0
}

trap cleanup EXIT
set -o pipefail

STDERR_FILE=$(mktemp)
add_cleanup rm -f "$STDERR_FILE"
exec 2> >(tee -a "$STDERR_FILE" >&2)

# vim: set sta sts=4 shiftwidth=4 sw=4 et ai :
