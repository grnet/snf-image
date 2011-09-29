base_name=$(subst -helper,,$(PACKAGE))

SUBDIRS = tasks

initdir=$(sysconfdir)
commondir=$(datarootdir)/$(base_name)

dist_doc_DATA = COPYING AUTHORS ChangeLog
dist_init_SCRIPTS = rc.local snf-passtohash.py
dist_init_DATA = common.sh

edit = sed \
	-e 's|@sysconfdir[@]|$(sysconfdir)|g' \
	-e 's|@localstatedir[@]|$(localstatedir)|g' \
	-e 's|@datarootdir[@]|$(datarootdir)|g' \
	-e 's|@base_name[@]|$(base_name)|g'
	-e 's|@RESIZE2FS[@]|$(RESIZE2FS)|g' \
	-e 's|@XMLSTARLET[@]|$(XMLSTARLET)|g'

%:%.in Makefile
	rm -f $@ $@.tmp
	srcdir=''; \
		   test -f ./$@.in || srcdir=$(srcdir)/; \
		   $(edit) $${srcdir}$@.in >$@.tmp
	mv $@.tmp $@

CLEANFILES = rc.local
