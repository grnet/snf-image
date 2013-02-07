get_img_dev() {
	echo /dev/xvdb
}

launch_helper() {
	local name helperid rc blockdev floppy

	blockdev="$1"
	floppy="$2"

	name=$(uuid)
    xm create /dev/null \
      kernel="$HELPER_KERNEL" ramdisk="$HELPER_INITRD"  root="/dev/xvda1" \
      extra="console=hvc0 hypervisor=$HYPERVISOR snf_image_activate_helper quiet ro boot=local" \
      disk="file:${HELPER_IMG},xvda,w" disk="phy:$blockdev,xvdb,w" \
      disk="file:$floppy,xvdc,r" vif="mac=aa:00:00:00:00:11,bridge=$XEN_BRIDGE" \
      memory="256" boot="c" vcpus=1 name="$name"

    if ! xenstore-exists snf-image-helper; then
        xenstore-write snf-image-helper ""
		#add_cleanup xenstore-rm snf-image-helper
    fi

    helperid=$(xm domid "$name")
    xenstore-write snf-image-helper/${helperid} ""
	add_cleanup xenstore-rm snf-image-helper/${helperid}
    xenstore-chmod snf-image-helper/${helperid} r0 w${helperid}

    brctl delif xenbr "vif${helperid}.0"

    socat EXEC:"./helper-monitor.py ${MONITOR_FD}" INTERFACE:vif${helperid}.0 &

	set +e

    $TIMEOUT -k $HELPER_HARD_TIMEOUT $HELPER_SOFT_TIMEOUT \
      socat EXEC:"xm console $name",pty STDOUT | sed -u 's|^|HELPER: |g'

	rc=$?
	set -e

    if [ $rc -ne 0 ]; then
        if [ $rc -eq 124 ];  then
            log_error "Image customization was terminated. Did not finish on time."
        elif [ $rc -eq 137 ]; then # (128 + SIGKILL)
            log_error "Image customization was killed. Did not finish on time."
        elif [ $rc -eq 141 ]; then # (128 + SIGPIPE)
            log_error "Image customization was terminated by a SIGPIPE."
            log_error "Maybe progress monitor has died unexpectedly."
        elif [ $rc -eq 125 ]; then
            log_error "Internal Error. Image customization could not start."
            log_error "timeout did not manage to run."
        else
            log_error "Image customization died unexpectedly (return code $rc)."
        fi
        exit 1
    else
        echo -n "$(date +%Y:%m:%d-%H:%M:%S.%N)" >&2
        log_info "Customization VM finished."
    fi

    result=$(xenstore-read snf-image-helper/$helperid)

    if [ "x$result" != "xSUCCESS" ]; then
        log_error "Image customization failed."
        exit 1
    fi

}

