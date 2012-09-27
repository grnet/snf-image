snf_export_DEV=/dev/vda

mk_snapshot() {

    "$QEMU_IMG" create -f qcow2 -b "$HELPER_IMG" "$snapshot"

}

launch_helper() {

  $TIMEOUT -k "$HELPER_HARD_TIMEOUT" "$HELPER_SOFT_TIMEOUT" \
    kvm -runas "$HELPER_USER" -drive file="$snapshot" \
    -drive file="$blockdev",format=raw,if=virtio,cache=none \
    -boot c -serial stdio -serial "file:$(printf "%q" "$result_file")" \
    -serial file:>(./helper-monitor.py ${MONITOR_FD}) \
    -fda "$floppy" -vga none -nographic -parallel none -monitor null \
    -kernel "$HELPER_KERNEL" -initrd "$HELPER_INITRD" \
    -append "quiet ro root=/dev/sda1 console=ttyS0,9600n8 \
             hypervisor=$HYPERVISOR snf_image_activate_helper" \
    2>&1 | sed -u 's|^|HELPER: |g'

}

get_helper_result() {

    result=$(sed 's|\r||g' "$result_file" | head -1)

}
