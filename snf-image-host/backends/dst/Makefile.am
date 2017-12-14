dbackendsdir=$(backendsdir)/dst
dbackendconfdir=$(confdir)/backends/dst

dist_dbackends_SCRIPTS = $(srcdir)/local $(srcdir)/uri
dist_dbackendconf_DATA = $(srcdir)/local.conf $(srcdir)/uri.conf \
			 $(srcdir)/local.priority $(srcdir)/uri.priority

export osdir dbackendsdir confdir

SUBDIRS = rbd

edit = sed \
	   -e 's|@osdir[@]|$(osdir)|g' \
	   -e 's|@localstatedir[@]|$(localstatedir)|g'


%:%.in Makefile
	rm -f $@ $@.tmp
	srcdir=''; \
		   test -f ./$@.in || srcdir=$(srcdir)/; \
		   $(edit) $${srcdir}$@.in >$@.tmp
	mv $@.tmp $@

CLEANFILES = $(dist_dbackends_SCRIPTS)
