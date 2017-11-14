pithosbackenddir=$(sbackendsdir)/pithos
sbackendconfdir=$(confdir)/backends/src

dist_pithosbackend_SCRIPTS = $(srcdir)/pithos $(srcdir)/pithcat
dist_sbackendconf_DATA=pithos.conf

edit = sed \
	   -e 's|@osdir[@]|$(osdir)|g' \
	   -e 's|@localstatedir[@]|$(localstatedir)|g' \
	   -e 's|@sysconfdir[@]|$(sysconfdir)|g'


%:%.in Makefile
	rm -f $@ $@.tmp
	srcdir=''; \
		   test -f ./$@.in || srcdir=$(srcdir)/; \
		   $(edit) $${srcdir}$@.in >$@.tmp
	mv $@.tmp $@

CLEANFILES = $(srcdir)/pithos $(dist_sbackendconf_DATA)

