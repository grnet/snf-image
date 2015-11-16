osname=snf-image
osdir=$(OS_DIR)/$(osname)
defaultdir=$(DEFAULT_DIR)
exampledir = $(datarootdir)/doc/$(PACKAGE)
variantsdir=${sysconfdir}/ganeti/snf-image/variants
xenscriptsdir=${sysconfdir}/xen/scripts

dist_os_SCRIPTS = ${srcdir}/create ${srcdir}/import ${srcdir}/export \
	${srcdir}/rename ${srcdir}/verify ${srcdir}/pithcat \
	${srcdir}/copy-monitor.py ${srcdir}/helper-monitor.py \
	${srcdir}/host-monitor.py ${srcdir}/decode-config.py

dist_os_DATA = ${srcdir}/ganeti_api_version ${srcdir}/parameters.list \
               ${srcdir}/variants.list ${srcdir}/xen-common.sh \
               ${srcdir}/kvm-common.sh

dist_xenscripts_SCRIPTS = ${srcdir}/vif-snf-image

dist_bin_SCRIPTS = snf-image-update-helper snf-image-create-helper

os_DATA = ${srcdir}/common.sh

example_DATA = defaults multistrap.conf version_pinning.pref kconfig-4.2.5-1~bpo8+1

edit = sed \
	   -e 's|@sysconfdir[@]|$(sysconfdir)|g' \
	   -e 's|@localstatedir[@]|$(localstatedir)|g' \
	   -e 's|@osdir[@]|$(osdir)|g' \
	   -e 's|@osname[@]|$(osname)|g' \
	   -e 's|@defaultdir[@]|$(defaultdir)|g' \
	   -e 's|@VERSION[@]|$(VERSION)|g' \
	   -e 's|@HELPER_PACKAGE_VERSION[@]|$(HELPER_PACKAGE_VERSION)|g' \
	   -e 's|@VERSION_CHECK[@]|$(VERSION_CHECK)|g' \
	   -e 's|@HELPER_DIR[@]|$(HELPER_DIR)|g' \
	   -e 's|@HELPER_URL[@]|$(HELPER_URL)|g' \
	   -e 's|@AWK[@]|$(AWK)|g' \
	   -e 's|@MKDIR_P[@]|$(MKDIR_P)|g' \
	   -e 's|@LOSETUP[@]|$(LOSETUP)|g' \
	   -e 's|@KPARTX[@]|$(KPARTX)|g' \
	   -e 's|@SFDISK[@]|$(SFDISK)|g' \
	   -e 's|@INSTALL_MBR[@]|$(INSTALL_MBR)|g' \
	   -e 's|@PROGRESS_MONITOR[@]|$(PROGRESS_MONITOR)|g' \
	   -e 's|@UNATTEND[@]|$(UNATTEND)|g' \
           -e 's|@MULTISTRAP_CONFIG[@]|$(MULTISTRAP_CONFIG)|g' \
           -e 's|@MULTISTRAP_APTPREFDIR[@]|$(MULTISTRAP_APTPREFDIR)|g'

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
	

CLEANFILES = $(os_DATA) $(dist_bin_SCRIPTS) defaults version_pinning.pref
