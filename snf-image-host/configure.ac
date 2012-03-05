AC_PREREQ(2.59)
AC_INIT(snf-image, 0.3.4, synnefo@lists.grnet.gr)

AC_CONFIG_AUX_DIR(autotools)
AC_CONFIG_SRCDIR(configure)

AM_INIT_AUTOMAKE([1.9 foreign tar-ustar -Wall -Wno-portability])
AM_INIT_AUTOMAKE([subdir-objects])

AC_ARG_ENABLE([pithos_backend],
   AS_HELP_STRING([--enable-pithos-backend],
    [enable support for pithos-hosted images])
)
AS_IF([test "x$enable_pithos_backend" = "xyes"],,
    [AC_MSG_NOTICE(pithos backend support not enabled)])
AM_CONDITIONAL(PITHOSIMGSUPPORT, [test "x$enable_pithos_backend" = "xyes"])

AC_ARG_ENABLE([network_backend],
   AS_HELP_STRING([--enable-network-backend],
    [enable support for network-hosted images
    (this depends on cURL)])
)
AS_IF([test "x$enable_network_backend" = "xyes"],,
    [AC_MSG_NOTICE(network backend support not enabled)])
AM_CONDITIONAL(NETWORKIMGSUPPORT, [test "x$enable_network_backend" = "xyes"])

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

# --with-helper-dir
AC_ARG_WITH([helper-dir],
    [AS_HELP_STRING([--with-helper-dir=DIR],
        [top-level directory to host the helper VM
        [LOCALSTATEDIR/lib/snf-image/helper]]
    )],
    [helper_dir="$withval"],
    [helper_dir="$localstatedir/lib/snf-image/helper"])
AC_SUBST(HELPER_DIR, $helper_dir)

# --with-helper-img
AC_ARG_WITH([helper-img],
    [AS_HELP_STRING([--with-helper-img=IMG_PATH],
        [Path to helper VM image [HELPERDIR/image]]
    )],
    [helper_img="$withval"],
    [helper_img="$helper_dir/image"])
AC_SUBST(HELPER_IMG, $helper_img)

# --with-helper-kernel
AC_ARG_WITH([helper-kernel],
    [AS_HELP_STRING([--with-helper-kernel=KERNEL_PATH],
        [Path to the helper VM kernel [HELPERDIR/kernel]]
    )],
    [helper_ernel="$withval"],
    [helper_kernel="$helper_dir/kernel"])
AC_SUBST(HELPER_KERNEL, ${helper_kernel})

# --with-helper-initrd..
AC_ARG_WITH([helper-initrd],
    [AS_HELP_STRING([--with-helper-initrd=INITRD_PATH],
        [Path to the helper VM initial ramdist [HELPERDIR/initrd]]
    )],
    [helper_initrd="$withval"],
    [helper_initrd="$helper_dir/initrd"])
AC_SUBST(HELPER_INITRD, ${helper_initrd})

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

# Check common programs
AC_PROG_INSTALL
AC_PROG_LN_S
AC_PROG_AWK
AC_PROG_MKDIR_P

AC_PATH_PROG(LOSETUP, [losetup], [], [$PATH:/usr/sbin:/sbin])
if test -z "$LOSETUP" ; then
  AC_MSG_ERROR([losetup not found in $PATH:/usr/sbin:/sbin])
fi

AC_PATH_PROG(KPARTX, [kpartx], [], [$PATH:/usr/sbin:/sbin])
if test -z "$KPARTX" ; then
  AC_MSG_ERROR([kpartx not found in $PATH:/usr/sbin:/sbin])
fi

AC_PATH_PROG(SFDISK, [sfdisk], [], [$PATH:/usr/sbin:/sbin])
if test -z "$SFDISK" ; then
  AC_MSG_ERROR([sfdisk not found in $PATH:/usr/sbin:/sbin])
fi

AC_PATH_PROG(QEMU_IMG, [qemu-img], [], [$PATH:/usr/sbin:/sbin])
if test -z "$QEMU_IMG" ; then
  AC_MSG_ERROR([qemu-img not found in $PATH:/usr/sbin:/sbin])
fi

AC_PATH_PROG(INSTALL_MBR, [install-mbr], [], [$PATH:/usr/sbin:/sbin])
if test -z "$INSTALL_MBR" ; then
  AC_MSG_ERROR([install-mbr not found in $PATH:/usr/sbin:/sbin])
fi

AC_PATH_PROG(TIMELIMIT, [timelimit], [], [$PATH:/usr/sbin:/sbin])
if test -z "$TIMELIMIT" ; then
  AC_MSG_ERROR([timelimit not found in $PATH:/usr/sbin:/sbin])
fi

if test "x$enable_network_backend" = "xyes" ; then
  AC_PATH_PROG(CURL, [curl], [], [$PATH:/usr/sbin:/sbin])
    if test -z "$CURL" ; then
      AC_MSG_ERROR([curl is needed for network backend support but was not \
      found in $PATH:/usr/sbin:/sbin]
      [To disable network backend support ommit --enable-network-backend])
    fi
fi

AC_CONFIG_FILES([
    Makefile
])

AC_OUTPUT

# vim: set sta sts=4 shiftwidth=4 sw=4 et ai :

