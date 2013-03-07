get_img_dev() {
	echo /dev/xvdb
}

#create_mac() {
#    # MAC address inside the range 00:16:3e:xx:xx:xx are reserved for Xen
#    echo  "aa:$(cat /proc/interrupts | md5sum | sed -r 's/^(.{10}).*$/\1/; s/([0-9a-f]{2})/\1:/g; s/:$//;')"
#}

launch_helper() {
    local name helperid rc blockdev floppy host_mac helper_mac

    blockdev="$1"
    floppy="$2"

	name=$(uuid)

    report_info "Starting customization VM..."
    echo "$($DATE +%Y:%m:%d-%H:%M:%S.%N) VM START" >&2

    xm create /dev/null \
      kernel="$HELPER_DIR/kernel-xen" ramdisk="$HELPER_DIR/initrd-xen" \
	  root="/dev/xvda1" memory="256" boot="c" vcpus=1 name="$name" \
      extra="console=hvc0 hypervisor=$HYPERVISOR snf_image_activate_helper \
	  ipv6.disable=1 rules_dev=/dev/xvdc ro boot=local helper_ip=10.0.0.1 \
          monitor_port=48888 init=/usr/bin/snf-image-helper" \
      disk="file:$HELPER_DIR/image,xvda,r" disk="phy:$blockdev,xvdb,w" \
      disk="file:$floppy,xvdc,r" vif="script=${XEN_SCRIPTS_DIR}/vif-snf-image"
    add_cleanup suppress_errors xm destroy "$name"

    if ! xenstore-exists snf-image-helper; then
        xenstore-write snf-image-helper ""
	#add_cleanup xenstore-rm snf-image-helper
    fi

    helperid=$(xm domid "$name")
    xenstore-write snf-image-helper/${helperid} ""
    add_cleanup xenstore-rm snf-image-helper/${helperid}
    xenstore-chmod snf-image-helper/${helperid} r0 w${helperid}

    filter='udp and dst port 48888 and dst host 10.0.0.255 and src host 10.0.0.1'
    $TIMEOUT -k $HELPER_HARD_TIMEOUT $HELPER_SOFT_TIMEOUT \
      ./helper-monitor.py -i "vif${helperid}.0" -f "$filter" ${MONITOR_FD} &
    monitor_pid=$!

    set +e
    $TIMEOUT -k $HELPER_HARD_TIMEOUT $HELPER_SOFT_TIMEOUT \
      socat EXEC:"xm console $name",pty STDOUT | sed -u 's|^|HELPER: |g'
    rc=$?
    set -e

    echo "$($DATE +%Y:%m:%d-%H:%M:%S.%N) VM STOP" >&2

    check_helper_rc "$rc"

    set +e
    wait "$monitor_pid"
    monitor_rc=$?
    set -e

    if [ $monitor_rc -ne 0 ]; then
       log_error "Helper VM monitoring failed"
       report_error "Helper VM monitoring failed"
       exit 1
    fi

    report_info "Checking customization status..."
    result=$(xenstore-read snf-image-helper/$helperid)
    report_info "Customization status is: $result"

    check_helper_result "$result"
}

# vim: set sta sts=4 shiftwidth=4 sw=4 et ai :
