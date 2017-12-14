rbdbackenddir=$(dbackendsdir)/rbd
dbackendconfdir=$(confdir)/backends/dst

dist_rbdbackend_SCRIPTS = $(srcdir)/rbd $(srcdir)/rbd_import
dist_dbackendconf_DATA=rbd.conf

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

CLEANFILES = $(srcdir)/rbd $(dist_dbackendconf_DATA)

