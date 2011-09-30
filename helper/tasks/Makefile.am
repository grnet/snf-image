tasksdir=${libdir}/$(base_name)/tasks

dist_tasks_SCRIPTS = \
		10ResizeUnmounted \
		30MountImage \
		40AddDeleteUnattendScript \
		40DeleteSSHKeys \
		40InstallUnattend \
		40ResizeMounted \
		40SELinuxAutorelabel \
		50AssignHostname \
		50ChangePassword \
		80UmountImage


edit = sed \
	   -e 's|@sysconfdir[@]|$(sysconfdir)|g' \
	   -e 's|@localstatedir[@]|$(localstatedir)|g' \
	   -e 's|@datarootdir[@]|$(datarootdir)|g' \
	   -e 's|@commondir[@]|$(commondir)|g'

%:%.in Makefile
	rm -f $@ $@.tmp
	srcdir=''; \
		   test -f ./$@.in || srcdir=$(srcdir)/; \
		   $(edit) $${srcdir}$@.in >$@.tmp
	mv $@.tmp $@

CLEANFILES = $(dist_tasks_SCRIPTS)
