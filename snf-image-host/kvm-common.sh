# Copyright (C) 2013, 2015 GRNET S.A. and individual contributors
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
	echo /dev/vdb
}

launch_helper() {
	local result_file result snapshot rc floppy blockdev

    blockdev="$1"
    floppy="$2"

    result_file=$(mktemp result.XXXXXX)
    add_cleanup rm "$result_file"

    report_info "Starting customization VM..."
    echo "$($DATE +%Y:%m:%d-%H:%M:%S.%N) VM START" >&2

    set +e

    if [ "x$HELPER_DEBUG" = "xyes" ]; then
        HELPER_DEBUG_ARG="snf_image_debug_helper"
    else
        HELPER_DEBUG_ARG=""
    fi


    $TIMEOUT -k "$HELPER_HARD_TIMEOUT" "$HELPER_SOFT_TIMEOUT" \
      $KVM -runas "$HELPER_USER" -drive file="$HELPER_DIR/image",format=raw,if=virtio,readonly \
      -drive file="$blockdev",format=raw,if=virtio,cache=none -m "$HELPER_MEMORY" \
      -boot c -serial stdio -serial "file:$(printf "%q" "$result_file")" \
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
