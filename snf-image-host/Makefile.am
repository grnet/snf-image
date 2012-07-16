if NETWORKIMGSUPPORT
network_backend_support=yes
else
network_backend_support=no
endif

osname=$(PACKAGE)
osdir=$(OS_DIR)/$(osname)
defaultdir=$(DEFAULT_DIR)
variantsdir=${sysconfdir}/ganeti/snf-image/variants

dist_os_SCRIPTS = ${srcdir}/create ${srcdir}/import ${srcdir}/export \
	${srcdir}/rename ${srcdir}/verify ${srcdir}/pithcat \
	${srcdir}/copy-monitor.py ${srcdir}/helper-monitor.py

dist_os_DATA = ${srcdir}/ganeti_api_version ${srcdir}/parameters.list \
               ${srcdir}/variants.list

dist_bin_SCRIPTS = snf-image-update-helper

os_DATA = common.sh

edit = sed \
	   -e 's|@sysconfdir[@]|$(sysconfdir)|g' \
	   -e 's|@localstatedir[@]|$(localstatedir)|g' \
	   -e 's|@osdir[@]|$(osdir)|g' \
	   -e 's|@osname[@]|$(osname)|g' \
	   -e 's|@defaultdir[@]|$(defaultdir)|g' \
	   -e 's|@HELPER_DIR[@]|$(HELPER_DIR)|g' \
	   -e 's|@HELPER_IMG[@]|$(HELPER_IMG)|g' \
	   -e 's|@HELPER_KERNEL[@]|$(HELPER_KERNEL)|g' \
	   -e 's|@HELPER_INITRD[@]|$(HELPER_INITRD)|g' \
	   -e 's|@HELPER_PKG[@]|$(HELPER_PKG)|g' \
	   -e 's|@AWK[@]|$(AWK)|g' \
	   -e 's|@MKDIR_P[@]|$(MKDIR_P)|g' \
	   -e 's|@LOSETUP[@]|$(LOSETUP)|g' \
	   -e 's|@KPARTX[@]|$(KPARTX)|g' \
	   -e 's|@SFDISK[@]|$(SFDISK)|g' \
	   -e 's|@QEMU_IMG[@]|$(QEMU_IMG)|g' \
	   -e 's|@INSTALL_MBR[@]|$(INSTALL_MBR)|g' \
	   -e 's|@PROGRESS_MONITOR[@]|$(PROGRESS_MONITOR)|g' \
	   -e 's|@UNATTEND[@]|$(UNATTEND)|g' \
	   -e 's|@progress_monitor_support[@]|$(progress_monitor_support)|g' \
	   -e 's|@network_backend_support[@]|$(network_backend_support)|g'

%:%.in Makefile
	rm -f $@ $@.tmp
	srcdir=''; \
		   test -f ./$@.in || srcdir=$(srcdir)/; \
		   $(edit) $${srcdir}$@.in >$@.tmp
	mv $@.tmp $@

install-exec-local:
	@mkdir_p@ "$(DESTDIR)$(osdir)"
	@mkdir_p@ "$(DESTDIR)$(variantsdir)"
	touch "$(DESTDIR)$(variantsdir)/default.conf"
	

CLEANFILES = $(os_DATA) $(dist_bin_SCRIPTS)
