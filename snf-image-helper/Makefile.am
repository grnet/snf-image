commondir=$(datarootdir)/$(PACKAGE)
networkingdir=$(libdir)/$(PACKAGE)/networking
scriptsdir=$(libdir)/$(PACKAGE)
tasksdir=$(scriptsdir)/tasks
export commondir networkingdir scriptsdir tasksdir

SUBDIRS = tasks networking

dist_doc_DATA = COPYING AUTHORS CONTRIBUTORS
dist_bin_SCRIPTS = snf-image-helper
dist_scripts_SCRIPTS= hashpwd.py inject-files.py decode-properties.py disklabel.py
dist_common_DATA = common.sh unattend.xml

edit = sed \
	-e 's|@commondir[@]|$(commondir)|g' \
	-e 's|@networkingdir[@]|$(networkingdir)|g' \
	-e 's|@scriptsdir[@]|$(scriptsdir)|g' \
	-e 's|@tasksdir[@]|$(tasksdir)|g'

%:%.in Makefile
	rm -f $@ $@.tmp
	srcdir=''; \
		   test -f ./$@.in || srcdir=$(srcdir)/; \
		   $(edit) $${srcdir}$@.in >$@.tmp
	mv $@.tmp $@

CLEANFILES = snf-image-helper common.sh
