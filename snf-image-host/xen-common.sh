snf_export_DEV=/dev/xvdb
HELPER_KERNEL=${HELPER_KERNEL}-xen
HELPER_INITRD=${HELPER_INITRD}-xen

mk_snapshot() {

    cp "$HELPER_IMG" "$snapshot"

}

launch_helper() {
    tail -f --pid=$$ "$result_file" | sed -u 's|^|HELPER: |' &
    $TIMEOUT -k $HELPER_HARD_TIMEOUT $HELPER_SOFT_TIMEOUT \
      screen -D -m -c /etc/screenrc bash -c 'xm create /dev/null \
      kernel="'$HELPER_KERNEL'" ramdisk="'$HELPER_INITRD'" \
      disk="file:'$snapshot',xvda,w" \
      disk="phy:'$blockdev',xvdb,w" \
      disk="file:'$floppy',xvdc1,w" \
      extra="console=hvc0 hypervisor='$HYPERVISOR' snf_image_activate_helper" \
      memory="256" root="/dev/xvda1 quiet ro boot=local" boot="c" vcpus=1 \
      name="snf-image-helper" -c > '$result_file''
}

get_helper_result() {

    result=$(sed 's|\r||g' "$result_file" | grep ^SUCCESS$)

}
