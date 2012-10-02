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

    brctl delif xenbr vif$helperid.0

    socat EXEC:"./helper-monitor.py ${MONITOR_FD}" INTERFACE:vif$helperid.0 &

    $TIMEOUT -k $HELPER_HARD_TIMEOUT $HELPER_SOFT_TIMEOUT \
      socat EXEC:"xm console $helper_name",pty STDOUT \
    | sed -u 's|^|HELPER: |g'

}

get_helper_result() {

    result=$(xenstore-read helper/$helperid)
    xenstore-rm helper/$helperid

}
