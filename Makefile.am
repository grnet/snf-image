if PROGMONSUPPORT
progress_monitor_support=yes
else
progress_monitor_support=no
endif

osdir=$(OS_DIR)/$(osname)
defaultdir=$(DEFAULT_DIR)
variantsdir=$(DESTDIR)${sysconfdir}/ganeti/snf-image/variants

dist_os_SCRIPTS = host/create
dist_os_DATA = ${srcdir}/host/ganeti_api_version ${srcdir}/host/parameters.list \
               ${srcdir}/host/variants.list

os_DATA = host/common.sh

edit = sed \
	   -e 's|@sysconfdir[@]|$(sysconfdir)|g' \
	   -e 's|@localstatedir[@]|$(localstatedir)|g' \
	   -e 's|@osdir[@]|$(osdir)|g' \
	   -e 's|@osname[@]|$(osname)|g' \
	   -e 's|@defaultdir[@]|$(defaultdir)|g' \
	   -e 's|@AWK[@]|$(AWK)|g' \
	   -e 's|@MKDIR_P[@]|$(MKDIR_P)|g' \
	   -e 's|@DUMP[@]|$(DUMP)|g' \
	   -e 's|@LOSETUP[@]|$(LOSETUP)|g' \
	   -e 's|@KPARTX[@]|$(KPARTX)|g' \
	   -e 's|@SFDISK[@]|$(SFDISK)|g' \
	   -e 's|@RESIZE2FS[@]|$(RESIZE2FS)|g' \
	   -e 's|@progress_monitor_support[@]|$(progress_monitor_support)|g' \
	   -e 's|@XMLSTARLET[@]|$(XMLSTARLET)|g' \
	   -e 's|@INSTALL_MBR[@]|$(INSTALL_MBR)|g' \
	   -e 's|@PROGRESS_MONITOR[@]|$(PROGRESS_MONITOR)|g'

host/common.sh: Makefile
	@mkdir_p@ host
	rm -f $@ $@.tmp
	srcdir=''; \
		   test -f ./$@.in || srcdir=$(srcdir)/; \
		   $(edit) $${srcdir}$@.in >$@.tmp
	mv $@.tmp $@

CLEANFILES = $(os_DATA)
