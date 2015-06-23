tasksdir=$(libdir)/$(PACKAGE)/tasks

dist_tasks_SCRIPTS = \
		10FixPartitionTable \
		20FilesystemResizeUnmounted \
		30MountImage \
		40AddSwap \
		40DeleteSSHKeys \
		40InstallUnattend \
		40SELinuxAutorelabel \
		41DisableRemoteDesktopConnections \
		50AssignHostname \
		50ChangePassword \
		50ConfigureNetwork \
		50FilesystemResizeMounted \
		60EnforcePersonality \
		80UmountImage

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

CLEANFILES = $(dist_tasks_SCRIPTS)

