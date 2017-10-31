AC_PREREQ(2.59)
m4_include([../version.m4])
AC_INIT(snf-image, devflow_version, synnefo@googlegroups.com)
AC_DEFINE_UNQUOTED(VERSION, "$devflow_version")

AC_CONFIG_AUX_DIR(autotools)
AC_CONFIG_SRCDIR(configure)

AM_INIT_AUTOMAKE([1.9 foreign tar-ustar -Wall -Wno-portability subdir-objects])

# --with-helper-url
AC_ARG_WITH([helper-url],
  [AS_HELP_STRING([--with-helper-url=URL],
      [URL to download the helper image from [https://cdn.synnefo.org/snf_image_helper_image-PROG_VERSION.tar.xz]])],
  [helper_url="$withval"],
  [helper_url="https://cdn.synnefo.org/snf_image_helper_image-$VERSION.tar.xz"]
)

AC_SUBST(HELPER_URL, $helper_url)

# --with-progress-monitor
AC_ARG_WITH([progress-monitor],
  [AS_HELP_STRING([--with-progress-monitor=PRGRM],
    [name of the progress-monitor program []])],
    [if test "$withval" != "yes" -a "$withval" != "no"; then
         AC_PATH_PROG(PROGRESS_MONITOR, ["$withval"], [], [$PATH:/usr/sbin:/sbin])
         if test -z "$PROGRESS_MONITOR" ; then
             AC_MSG_FAILURE([Could not find progress-monitor: $withval.])
         fi
     elif test "$withval" != "no"; then
         AC_MSG_ERROR([you must specify a value for progress-monitor if --with-progress-monitor is specified])
    fi]
)

# --with-unattend-file
AC_ARG_WITH([unattend-file],
  [AS_HELP_STRING([--with-unattend-file=UNATTEND_PATH],
    [path to unattend.xml Windows setup file []])],
    [if test "$withval" != "yes" -a "$withval" != "no"; then
	AC_SUBST(UNATTEND, "$withval")
        AC_MSG_NOTICE(using unattend file: $withval)
     elif test "$withval" != "no"; then
         AC_MSG_ERROR([you must specify an Unattend.xml file if --with-unattend-file is specified])
    fi]
)

# --with-multistrap-config
AC_ARG_WITH([multistrap-config],
  [AS_HELP_STRING([--with-multistrap-config=MULTISTRAP_CONFIG_PATH],
      [path to a multistrap configuration file
      [SYSCONFDIR/snf-image/multistrap.conf]]
    )],
    [if test "$withval" != "yes" -a "$withval" != "no"; then
	multistrap_config="$withval"
        AC_MSG_NOTICE(using multistrap configuration file: $withval)
     elif test "$withval" != "no"; then
         AC_MSG_ERROR([you must specify an configuration file if --with-multistrap-config is specified])
    fi],
    [multistrap_config="$sysconfdir/snf-image/multistrap.conf"]
)
AC_SUBST(MULTISTRAP_CONFIG, $multistrap_config)

# --with-xen-cmd
AC_ARG_WITH([xen-cmd],
  [AS_HELP_STRING([--with-xen-cmd=XEN_CLI_TOOL],
      [the default Xen CLI tool
      [xl]]
    )],
    [if test "$withval" != "yes" -a "$withval" != "no"; then
        if test "$withval" != xm -a "$withval" != xl; then
            AC_MSG_ERROR([valid values for --with-xen-cmd are 'xm' and 'xl'])
        fi
	xen_cmd="$withval"
        AC_MSG_NOTICE(using Xen CLI tool: $withval)
     elif test "$withval" != "no"; then
         AC_MSG_ERROR([you must specify a CLI tool if --with-xen-cmd is specified])
    fi],
    [xen_cmd="xl"]
)

AC_SUBST(XEN_CMD, $xen_cmd)

# --with-multistrap-aptprefdir
AC_ARG_WITH([multistrap-aptprefdir],
  [AS_HELP_STRING([--with-multistrap-aptprefdir=MULTISTRAP_APTPREFDIR],
      [path to a directory where preferences files for apt are hosted. Those files will be used during multistrap
      [SYSCONFDIR/snf-image/apt.pref.d]]
    )],
    [if test "$withval" != "yes" -a "$withval" != "no"; then
	multistrap_aptprefdir="$withval"
        AC_MSG_NOTICE(using apt preferences directory for multistrap: $withval)
     elif test "$withval" != "no"; then
         AC_MSG_ERROR([you must specify a directory if --with-multistrap-aptprefdir is specified])
    fi],
    [multistrap_aptprefdir="$sysconfdir/snf-image/apt.pref.d"]
)
AC_SUBST(MULTISTRAP_APTPREFDIR, $multistrap_aptprefdir)

# --with-helper-dir
AC_ARG_WITH([helper-dir],
    [AS_HELP_STRING([--with-helper-dir=DIR],
        [top-level directory to host the helper VM
        [LOCALSTATEDIR/lib/snf-image/helper]]
    )],
    [helper_dir="$withval"],
    [helper_dir="$localstatedir/lib/snf-image/helper"])
AC_SUBST(HELPER_DIR, $helper_dir)

# --with-os-dir=...
AC_ARG_WITH([os-dir],
    [AS_HELP_STRING([--with-os-dir=DIR],
        [top-level OS directory under which to install [DATADIR/ganeti/os]]
    )],
    [os_dir="$withval"],
    [os_dir="$datadir/ganeti/os"])
AC_SUBST(OS_DIR, $os_dir)

# --with-default-dir=...
AC_ARG_WITH([default-dir],
    [AS_HELP_STRING([--with-default-dir=DIR],
        [top-level default config directory under which to install]
        [ [SYSCONFDIR/default]]
    )],
    [default_dir="$withval"],
    [default_dir="$sysconfdir/default"])
AC_SUBST(DEFAULT_DIR, $default_dir)

# --with-helper-package-version=
AC_ARG_WITH([helper-package-version],
    [AS_HELP_STRING([--with-helper-package-version=VERSION],
                    [snf-image-helper package version to use for the helper image (default autodetect)])],
    [helper_package_version="$withval"],
    [helper_package_version="$VERSION*"])
AC_SUBST(HELPER_PACKAGE_VERSION, $helper_package_version)


# Check common programs
AC_PROG_INSTALL
AC_PROG_LN_S
AC_PROG_AWK
AC_PROG_MKDIR_P

AC_PATH_PROG(LOSETUP, [losetup], [], [$PATH:/usr/sbin:/sbin])
if test -z "$LOSETUP" ; then
  AC_MSG_ERROR([losetup not found in $PATH:/usr/sbin:/sbin])
fi

AC_PATH_PROG(INSTALL_MBR, [install-mbr], [], [$PATH:/usr/sbin:/sbin])
if test -z "$INSTALL_MBR" ; then
  AC_MSG_ERROR([install-mbr not found in $PATH:/usr/sbin:/sbin])
fi

AC_PATH_PROG(TIMEOUT, [timeout], [], [$PATH:/usr/sbin:/sbin])
if test -z "$TIMEOUT" ; then
  AC_MSG_ERROR([timeout not found in $PATH:/usr/sbin:/sbin])
fi

AC_PATH_PROG(CURL, [curl], [], [$PATH:/usr/sbin:/sbin])
if test -z "$CURL" ; then
  AC_MSG_ERROR([curl not found in $PATH:/usr/sbin:/sbin])
fi

AC_PATH_PROG(PARTED, [parted], [], [$PATH:/usr/sbin:/sbin])
if test -z "$PARTED" ; then
  AC_MSG_ERROR([parted not found in $PATH:/usr/sbin:/sbin])
fi

#Python Dependencies
AM_PATH_PYTHON(2.6)

AC_PYTHON_MODULE(prctl, t)
AC_PYTHON_MODULE(scapy, t)

AC_CONFIG_FILES([
    Makefile
    backends/Makefile
    backends/src/Makefile
    backends/src/pithos/Makefile
    backends/dst/Makefile
])

AC_OUTPUT

# vim: set sta sts=4 shiftwidth=4 sw=4 et ai :

