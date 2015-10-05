# Copyright (C) 2013-2015 GRNET S.A.
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

assign_disk_devices_to() {
    local varname
    varname="$1"

    eval $varname=\(\)

    set -- b c d e f g h e j k l m n

    for ((i = 0; i < DISK_COUNT; i++)); do
        eval $varname+=\(\"/dev/vd$1\"\); shift
    done
}

launch_helper() {
    local result_file result snapshot rc floppy i disk_path disks

    floppy="$1"

    result_file=$(mktemp result.XXXXXX)
    add_cleanup rm "$result_file"

    report_info "Starting customization VM..."
    echo "$($DATE +%Y:%m:%d-%H:%M:%S.%N) VM START" >&2

    disks=""
    for ((i=0; i < DISK_COUNT; i++)); do
        eval disk_path=\"\$DISK_${i}_PATH\"
        disks+=" -drive file=$disk_path,format=raw,if=virtio,cache=none"
    done

    set +e

    $TIMEOUT -k "$HELPER_HARD_TIMEOUT" "$HELPER_SOFT_TIMEOUT" \
      $KVM -runas "$HELPER_USER" \
      -drive file="$HELPER_DIR/image",format=raw,if=virtio,readonly \
      $disks -m "$HELPER_MEMORY" -boot c -serial stdio \
      -serial "file:$(printf "%q" "$result_file")" \
      -serial file:>(./helper-monitor.py ${MONITOR_FD}) \
      -drive file="$floppy",if=floppy -vga none -nographic -parallel none -monitor null \
      -kernel "$HELPER_DIR/kernel" -initrd "$HELPER_DIR/initrd" \
      -append "quiet ro root=/dev/vda console=ttyS0,9600n8 \
             hypervisor=$HYPERVISOR snf_image_activate_helper \
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
