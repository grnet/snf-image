AC_PREREQ(2.59)
m4_include([../version.m4])
AC_INIT(snf-image-helper, devflow_version, synnefo@googlegroups.com)

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

AC_PATH_PROG(TUNE2FS, [tune2fs], [], [$PATH:/usr/sbin:/sbin])
if test -z "$TUNE2FS" ; then
  AC_MSG_ERROR([tune2fs not found in $PATH])
fi

AC_PATH_PROG(RESIZE2FS, [resize2fs], [], [$PATH:/usr/sbin:/sbin])
if test -z "$RESIZE2FS" ; then
  AC_MSG_ERROR([resize2fs not found in $PATH])
fi

AC_PATH_PROG(PARTED, [parted], [], [$PATH:/usr/sbin:/sbin])
if test -z "$PARTED" ; then
  AC_MSG_ERROR([parted not found in $PATH])
fi

AC_PATH_PROG(SFDISK, [sfdisk], [], [$PATH:/usr/sbin:/sbin])
if test -z "$SFDISK" ; then
  AC_MSG_ERROR([sfdisk not found in $PATH])
fi

AC_PATH_PROG(SGDISK, [sgdisk], [], [$PATH:/usr/sbin:/sbin])
if test -z "$SGDISK" ; then
  AC_MSG_ERROR([SGDISK not found in $PATH])
fi

AC_PATH_PROG(EATMYDATA, [eatmydata], [], [$PATH:/usr/sbin:/sbin])
if test -z "$EATMYDATA" ; then
  AC_MSG_ERROR([EATMYDATA not found in $PATH])
fi

AC_PATH_PROG(HIVEXGET, [hivexget], [], [$PATH:/usr/sbin:/sbin])
if test -z "$HIVEXGET" ; then
  AC_MSG_ERROR([hivexget not found in $PATH])
fi

AC_PATH_PROG(HIVEXREGEDIT, [hivexregedit], [], [$PATH:/usr/sbin:/sbin])
if test -z "$HIVEXREGEDIT" ; then
  AC_MSG_ERROR([hivexregedit not found in $PATH])
fi

AC_CONFIG_FILES([
    Makefile
    tasks/Makefile
])
AC_OUTPUT

# vim: set sta sts=4 shiftwidth=4 sw=4 et ai :
