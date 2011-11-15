AC_PREREQ(2.59)
AC_INIT(snf-image-helper, 0.2, synnefo@lists.grnet.gr)

AC_CONFIG_AUX_DIR(autotools)
AC_CONFIG_SRCDIR(configure)

AM_INIT_AUTOMAKE([1.9 foreign tar-ustar -Wall -Wno-portability])
AM_INIT_AUTOMAKE([subdir-objects])

# Check common programs
AC_PROG_INSTALL
AC_PROG_LN_S
AC_PROG_AWK
AC_PROG_MKDIR_P

AC_PATH_PROG(XMLSTARLET, [xmlstarlet], [], [$PATH:/usr/sbin:/sbin])
if test -z "$XMLSTARLET" ; then
  AC_MSG_ERROR([xmlstarlet not found in $PATH])
fi

AC_PATH_PROG(RESIZE2FS, [resize2fs], [], [$PATH:/usr/sbin:/sbin])
if test -z "$RESIZE2FS" ; then
  AC_MSG_ERROR([resize2fs not found in $PATH])
fi

AC_PATH_PROG(PARTED, [parted], [], [$PATH:/usr/sbin:/sbin])
if test -z "$PARTED" ; then
  AC_MSG_ERROR([parted not found in $PATH])
fi

AC_PATH_PROG(REGLOOKUP, [reglookup], [], [$PATH:/usr/sbin:/sbin])
if test -z "$REGLOOKUP" ; then
  AC_MSG_ERROR([reglookup not found in $PATH])
fi

AC_PATH_PROG(CHNTPW, [chntpw], [], [$PATH:/usr/sbin:/sbin])
if test -z "$CHNTPW" ; then
  AC_MSG_ERROR([chntpw not found in $PATH])
fi

AC_CONFIG_FILES([
    Makefile
    tasks/Makefile
])
AC_OUTPUT

# vim: set sta sts=4 shiftwidth=4 sw=4 et ai :
