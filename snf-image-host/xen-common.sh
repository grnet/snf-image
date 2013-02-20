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
	  ipv6.disable=1 rules_dev=/dev/xvdc ro boot=local init=/usr/bin/snf-image-helper" \
      disk="file:$HELPER_DIR/image,xvda,r" disk="phy:$blockdev,xvdb,w" \
      disk="file:$floppy,xvdc,r" vif="script=${XEN_SCRIPTS_DIR}/vif-snf-image"

    if ! xenstore-exists snf-image-helper; then
        xenstore-write snf-image-helper ""
		#add_cleanup xenstore-rm snf-image-helper
    fi

    helperid=$(xm domid "$name")
    xenstore-write snf-image-helper/${helperid} ""
    add_cleanup xenstore-rm snf-image-helper/${helperid}
    xenstore-chmod snf-image-helper/${helperid} r0 w${helperid}

    socat EXEC:"./helper-monitor.py ${MONITOR_FD}" INTERFACE:vif${helperid}.0 &

    set +e

    $TIMEOUT -k $HELPER_HARD_TIMEOUT $HELPER_SOFT_TIMEOUT \
      socat EXEC:"xm console $name",pty STDOUT | sed -u 's|^|HELPER: |g'

    rc=$?
    set -e

    echo "$($DATE +%Y:%m:%d-%H:%M:%S.%N) VM STOP" >&2
    if [ $rc -ne 0 ]; then
        if [ $rc -eq 124 ];  then
            log_error "Customization VM was terminated. Did not finish on time."
            report_error "Image customization failed. Did not finish on time."
        elif [ $rc -eq 137 ]; then # (128 + SIGKILL)
            log_error "Customization VM was killed. Did not finish on time."
            report_error "Image customization failed. Did not finish on time."
        elif [ $rc -eq 141 ]; then # (128 + SIGPIPE)
            log_error "Customization VM was terminated by a SIGPIPE."
            log_error "Maybe progress monitor has died unexpectedly."
        elif [ $rc -eq 125 ]; then
            log_error "Internal Error. Image customization could not start."
            log_error "timeout did not manage to run."
        else
            log_error "Customization VM died unexpectedly (return code $rc)."
        fi
        exit 1
    else
        report_info "Customization VM exited normally."
    fi

    report_info "Checking customization status..."
    result=$(xenstore-read snf-image-helper/$helperid)
    report_info "Customization status is: $result"

    if [ "x$result" != "xSUCCESS" ]; then
        log_error "Image customization failed."
        report_error "Image customization failed."
        exit 1
    fi
}

# vim: set sta sts=4 shiftwidth=4 sw=4 et ai :
