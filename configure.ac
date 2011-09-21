AC_PREREQ(2.59)
AC_INIT(snf-image, 0.1, synnefo@lists.grnet.gr)

AC_CONFIG_AUX_DIR(autotools)
AC_CONFIG_SRCDIR(configure)

AM_INIT_AUTOMAKE([1.9 foreign tar-ustar -Wall -Wno-portability])
AM_INIT_AUTOMAKE([subdir-objects])

# --with-progress-monitor
AC_ARG_WITH([progress-monitor],
  [AS_HELP_STRING([--with-progress-monitor=PRGRM_PATH],
    [path to progress-monitor program]
    [[snf-progress-monitor]])],
    [if test "$withval" = "yes" ; then
    AC_PATH_PROG(PROGRESS_MONITOR, [snf-progress-monitor], [], [$PATH:/usr/sbin:/sbin])
    if test -z "$PROGRESS_MONITOR" ; then
        AC_MSG_FAILURE([Could not find snf-progress-monitor.])
    fi
   else
       PROGRESS_MONITOR="$withval"
   fi],
   [AC_MSG_NOTICE(progress-monitor support not enabled)]
)

AM_CONDITIONAL(PROGMONSUPPORT, [test -n "$PROGRESS_MONITOR"])


# --with-os-dir=...
AC_ARG_WITH([os-dir],
    [AS_HELP_STRING([--with-os-dir=DIR],
        [top-level OS directory under which to install]
        [ (default is $datadir/ganeti/os)]
    )],
    [os_dir="$withval"],
    [os_dir="$datadir/ganeti/os"])
AC_SUBST(OS_DIR, $os_dir)

# --with-default-dir=...
AC_ARG_WITH([default-dir],
    [AS_HELP_STRING([--with-default-dir=DIR],
        [top-level default config directory under which to install]
        [ (default is $sysconfdir/default)]
    )],
    [default_dir="$withval"],
    [default_dir="$sysconfdir/default"])
AC_SUBST(DEFAULT_DIR, $default_dir)

# Check common programs
AC_PROG_INSTALL
AC_PROG_LN_S
AC_PROG_AWK
AC_PROG_MKDIR_P

AC_PATH_PROG(LOSETUP, [losetup], [], [$PATH:/usr/sbin:/sbin])
if test -z "$LOSETUP" ; then
  AC_MSG_ERROR([losetup not found in $PATH])
fi

AC_PATH_PROG(KPARTX, [kpartx], [], [$PATH:/usr/sbin:/sbin])
if test -z "$KPARTX" ; then
  AC_MSG_ERROR([kpartx not found in $PATH])
fi

AC_PATH_PROG(SFDISK, [sfdisk], [], [$PATH:/usr/sbin:/sbin])
if test -z "$SFDISK" ; then
  AC_MSG_ERROR([sfdisk not found in $PATH])
fi

AC_CONFIG_FILES([
    Makefile
])

AC_OUTPUT

# vim: set sta sts=4 shiftwidth=4 sw=4 et ai :

