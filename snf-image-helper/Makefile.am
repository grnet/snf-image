commondir=$(datarootdir)/$(PACKAGE)
scriptsdir=$(libdir)/$(PACKAGE)
tasksdir=$(scriptsdir)/tasks
export commondir scriptsdir tasksdir

SUBDIRS = tasks

dist_doc_DATA = COPYING AUTHORS
dist_bin_SCRIPTS = snf-image-helper
dist_scripts_SCRIPTS= hashpwd.py inject-files.py decode-properties.py disklabel.py
dist_common_DATA = common.sh unattend.xml

edit = sed \
	-e 's|@commondir[@]|$(commondir)|g' \
	-e 's|@scriptsdir[@]|$(scriptsdir)|g' \
	-e 's|@tasksdir[@]|$(tasksdir)|g' \
	-e 's|@RESIZE2FS[@]|$(RESIZE2FS)|g' \
	-e 's|@XMLSTARLET[@]|$(XMLSTARLET)|g'

%:%.in Makefile
	rm -f $@ $@.tmp
	srcdir=''; \
		   test -f ./$@.in || srcdir=$(srcdir)/; \
		   $(edit) $${srcdir}$@.in >$@.tmp
	mv $@.tmp $@

CLEANFILES = snf-image-helper
