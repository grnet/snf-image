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
      extra="console=hvc0 hypervisor=$HYPERVISOR snf_image_activate_helper" \
      disk="file:$snapshot,xvda,w" \
      disk="phy:$blockdev,xvdb,w" \
      disk="file:$floppy,xvdc1,w" \
      vif="mac=aa:00:00:00:00:11,bridge=xenbr" \
      memory="256" root="/dev/xvda1 quiet ro boot=local" boot="c" vcpus=1 \
      name="$helper_name"

    if [ ! $(xenstore-exists helper) ]; then
        xenstore-write helper ""
    fi
    helperid=$(xm domid $helper_name)
    xenstore-write helper/$helperid ""
    xenstore-chmod helper/$helperid r0 w$helperid

    tail -f --pid=$$ "$result_file" | sed -u 's|^|HELPER: |' &

    brctl delif xenbr vif$helperid.0
    screen -d -m -c /etc/screenrc bash -c 'socat STDIO INTERFACE:vif'$helperid'.0  | ./helper-monitor.py 1 > '$monitor_pipe' '

    $TIMEOUT -k $HELPER_HARD_TIMEOUT $HELPER_SOFT_TIMEOUT \
      screen -D -m -c /etc/screenrc bash -c ' xm console '$helper_name' > '$result_file''

}

get_helper_result() {

    result=$(xenstore-read helper/$helperid)
    xenstore-rm helper/$helperid

}
