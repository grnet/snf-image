networkingdir=$(libdir)/$(PACKAGE)/networking

dist_networking_SCRIPTS = ifupdown.sh ifcfg.sh freebsd.sh openbsd.sh netbsd.sh nm.sh cloud-init.sh

edit = sed \
           -e 's|@sysconfdir[@]|$(sysconfdir)|g' \
           -e 's|@localstatedir[@]|$(localstatedir)|g' \
           -e 's|@datarootdir[@]|$(datarootdir)|g' \
           -e 's|@commondir[@]|$(commondir)|g' \
           -e 's|@networkingdir[@]|$(networkingdir)|g' \
           -e 's|@scriptsdir[@]|$(scriptsdir)|g'

%:%.in Makefile
	rm -f $@ $@.tmp
	srcdir=''; \
		   test -f ./$@.in || srcdir=$(srcdir)/; \
		   $(edit) $${srcdir}$@.in >$@.tmp
	mv $@.tmp $@

CLEANFILES = $(dist_networking_SCRIPTS)
