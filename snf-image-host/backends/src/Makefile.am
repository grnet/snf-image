sbackendsdir=$(backendsdir)/src
sbackendconfdir=$(confdir)/backends/src/

dist_sbackends_SCRIPTS = ${srcdir}/local ${srcdir}/null ${srcdir}/network
dist_sbackendconf_DATA=local.conf

export osdir sbackendsdir confdir

SUBDIRS = pithos

edit = sed \
	   -e 's|@osdir[@]|$(osdir)|g' \
	   -e 's|@localstatedir[@]|$(localstatedir)|g'


%:%.in Makefile
	rm -f $@ $@.tmp
	srcdir=''; \
		   test -f ./$@.in || srcdir=$(srcdir)/; \
		   $(edit) $${srcdir}$@.in >$@.tmp
	mv $@.tmp $@

CLEANFILES = $(dist_sbackends_SCRIPTS) $(dist_sbackendconf_DATA)
