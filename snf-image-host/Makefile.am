osname=snf-image
osdir=$(OS_DIR)/$(osname)
backendsdir=$(osdir)/backends
sbackendsdir=$(backendsdir)/src
exampledir=$(datarootdir)/doc/$(PACKAGE)
confdir=$(sysconfdir)/snf-image/
aptprefdir=$(confdir)/apt.pref.d
variantsdir=$(sysconfdir)/ganeti/snf-image/variants
xenscriptsdir=$(sysconfdir)/xen/scripts

export osdir confdir backendsdir sbackendsdir

SUBDIRS = backends

dist_os_SCRIPTS = $(srcdir)/create $(srcdir)/import $(srcdir)/export \
	$(srcdir)/rename $(srcdir)/verify \
	$(srcdir)/copy-monitor.py $(srcdir)/helper-monitor.py \
	$(srcdir)/host-monitor.py $(srcdir)/decode-config.py

dist_os_DATA = $(srcdir)/ganeti_api_version $(srcdir)/parameters.list \
               $(srcdir)/variants.list $(srcdir)/xen-common.sh \
               $(srcdir)/kvm-common.sh $(srcdir)/unattend.xml.in \
               $(srcdir)/sysprep.inf.in $(srcdir)/ms-timezone-indexes.txt \
	       $(srcdir)/common.sh

dist_xenscripts_SCRIPTS = $(srcdir)/vif-snf-image

dist_bin_SCRIPTS = snf-image-update-helper snf-image-create-helper

dist_conf_DATA = snf-image.conf multistrap.conf

dist_aptpref_DATA = version_pinning.pref

example_DATA = kconfig-4.9.30-2+deb9u2.1.snf.image.helper.1

edit = sed \
	   -e 's|@sysconfdir[@]|$(sysconfdir)|g' \
	   -e 's|@localstatedir[@]|$(localstatedir)|g' \
	   -e 's|@confdir[@]|$(confdir)|g' \
	   -e 's|@osdir[@]|$(osdir)|g' \
	   -e 's|@backendsdir[@]|$(backendsdir)|g' \
	   -e 's|@sbackendsdir[@]|$(sbackendsdir)|g' \
	   -e 's|@osname[@]|$(osname)|g' \
	   -e 's|@VERSION[@]|$(VERSION)|g' \
	   -e 's|@HELPER_PACKAGE_VERSION[@]|$(HELPER_PACKAGE_VERSION)|g' \
	   -e 's|@HELPER_DIR[@]|$(HELPER_DIR)|g' \
	   -e 's|@HELPER_URL[@]|$(HELPER_URL)|g' \
	   -e 's|@AWK[@]|$(AWK)|g' \
	   -e 's|@MKDIR_P[@]|$(MKDIR_P)|g' \
	   -e 's|@LOSETUP[@]|$(LOSETUP)|g' \
	   -e 's|@INSTALL_MBR[@]|$(INSTALL_MBR)|g' \
	   -e 's|@PROGRESS_MONITOR[@]|$(PROGRESS_MONITOR)|g' \
	   -e 's|@UNATTEND[@]|$(UNATTEND)|g' \
	   -e 's|@XEN_CMD[@]|$(XEN_CMD)|g' \
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
	

CLEANFILES = $(srcdir)/common.sh $(dist_bin_SCRIPTS) $(srcdir)/snf-image.conf
