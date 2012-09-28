snf_export_DEV=/dev/xvdb
HELPER_KERNEL=${HELPER_KERNEL}-xen
HELPER_INITRD=${HELPER_INITRD}-xen

mk_snapshot() {

    cp "$HELPER_IMG" "$snapshot"

}

launch_helper() {

    helper_name=helper$$
    xm create /dev/null \
      kernel="$HELPER_KERNEL" ramdisk="$HELPER_INITRD" \
      disk="file:$snapshot,xvda,w" \
      disk="phy:$blockdev,xvdb,w" \
      disk="file:$floppy,xvdc1,w" \
      extra="console=hvc0 hypervisor=$HYPERVISOR snf_image_activate_helper" \
      memory="256" root="/dev/xvda1 quiet ro boot=local" boot="c" vcpus=1 \
      name="$helper_name"

    if ! xenstore-exists helper;
        xenstore-write helper ""
    fi
    helperid=$(xm domid $helper_name)
    xenstore-write helper/$helperid ""
    xenstore-chmod helper/$helperid r0 w$helperid

    tail -f --pid=$$ "$result_file" | sed -u 's|^|HELPER: |' &
    $TIMEOUT -k $HELPER_HARD_TIMEOUT $HELPER_SOFT_TIMEOUT \
      screen -D -m -c /etc/screenrc bash -c ' xm console '$helper_name' > '$result_file''
}

get_helper_result() {

    result=$(xenstore-read helper/$helperid)

}
