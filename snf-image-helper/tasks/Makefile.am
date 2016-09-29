tasksdir=$(libdir)/$(PACKAGE)/tasks

dist_tasks_SCRIPTS = \
		10FixPartitionTable \
		20FilesystemResizeUnmounted \
		30MountImage \
		35InstallUnattend \
		40FilesystemResizeMounted \
		50AddSwap \
		50AssignHostname \
		50ChangeMachineId \
		50ChangePassword \
		50ConfigureNetwork \
		50DeleteSSHKeys \
		50DisableRemoteDesktopConnections \
		50SELinuxAutorelabel \
		60EnforcePersonality \
		70RunCustomTask \
		80UmountImage \
		81FilesystemResizeAfterUmount


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

