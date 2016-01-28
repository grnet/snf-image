# Copyright (C) 2013-2016 GRNET S.A. and individual contributors
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

get_img_dev() {
    local idx=$1
    local letters=( a b c d e f g h e j k l m n )

    case $disk_type in
        # The helper's root disk is always paravirtual and thus /dev/vda
        # will be occupied.
        paravirtual) echo /dev/vd${letters[$idx+1]};;
        scsi-generic|scsi-block|scsi-hd|scsi) echo /dev/sd${letters[$idx]};;
    esac
}

get_img_driver() {
    case $disk_type in
        paravirtual) echo virtio-blk-pci;;
        scsi|scsi-hd) echo scsi-hd;;
        scsi-block) echo scsi-block;;
        scsi-generic) echo scsi-generic;;
    esac
}

assign_disk_devices_to() {
    local varname dev i

    varname="$1"

    # This will declare the given variable as an array
    eval $varname=\(\)

    # For DISK_COUNT=3, disk_type=paravirtual, and varname=snf_export_DEV
    # this will create snf_export_DEV array of ( /dev/vdb /dev/vdc /dev/vdd )
    for ((i = 0; i < DISK_COUNT; i++)); do
        dev=$(get_img_dev $i)
        eval $varname+=\(\"$dev\"\)
    done
}

launch_helper() {
    local result_file result snapshot rc floppy i disks

    floppy="$1"

    result_file=$(mktemp --tmpdir result.XXXXXX)
    add_cleanup rm "$result_file"

    report_info "Starting customization VM..."
    echo "$($DATE +%Y:%m:%d-%H:%M:%S.%N) VM START" >&2

    disks=""
    for ((i=0; i < DISK_COUNT; i++)); do
        disks+=" -drive file=$(find_disk $i),format=raw,if=none,cache=none,id=drive$i"
        disks+=" -device $(get_img_driver),id=disk$i,drive=drive$i"
    done

    set +e

    if [ "x$HELPER_DEBUG" = "xyes" ]; then
        HELPER_DEBUG_ARG="snf_image_debug_helper"
    else
        HELPER_DEBUG_ARG=""
    fi

    if [[ "$disk_type" =~ ^scsi ]]; then
        EXTRA_CONTROLLER_ARG="-device virtio-scsi-pci"
    fi

    $TIMEOUT -k "$HELPER_HARD_TIMEOUT" "$HELPER_SOFT_TIMEOUT" \
      $KVM -runas "$HELPER_USER" \
      -drive file="$HELPER_DIR/image",format=raw,if=none,id=helper,readonly \
      -device virtio-blk-pci,id=helper,drive=helper \
      $EXTRA_CONTROLLER_ARG $disks \
      -m "$HELPER_MEMORY" -boot c -serial stdio \
      -serial "file:$(printf "%q" "$result_file")" \
      -serial file:>(./helper-monitor.py ${MONITOR_FD}) \
      -serial pty \
      -drive file="$floppy",if=floppy -vga none -nographic -parallel none -monitor null \
      -kernel "$HELPER_DIR/kernel" -initrd "$HELPER_DIR/initrd" \
      -append "quiet ro root=/dev/vda console=ttyS0,9600n8 \
             hypervisor=$HYPERVISOR snf_image_activate_helper \
             $HELPER_DEBUG_ARG \
	     rules_dev=/dev/fd0 init=/usr/bin/snf-image-helper" \
      2>&1 | sed -u 's|^|HELPER: |g'

    rc=$?
    set -e
    echo "$($DATE +%Y:%m:%d-%H:%M:%S.%N) VM STOP" >&2

    check_helper_rc "$rc"

    report_info "Checking customization status..."
    # Read the first line. This will remove \r and \n chars
    result=$(sed 's|\r||g' "$result_file" | head -1)
    report_info "Customization status is: $result"

    check_helper_result "$result"
}

# vim: set sta sts=4 shiftwidth=4 sw=4 et ai :
