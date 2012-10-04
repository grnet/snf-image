AC_PREREQ(2.59)
AC_INIT(snf-image, 0.6, synnefo@lists.grnet.gr)

AC_CONFIG_AUX_DIR(autotools)
AC_CONFIG_SRCDIR(configure)

AM_INIT_AUTOMAKE([1.9 foreign tar-ustar -Wall -Wno-portability])
AM_INIT_AUTOMAKE([subdir-objects])

AC_ARG_ENABLE([network_backend],
   AS_HELP_STRING([--enable-network-backend],
    [enable support for network-hosted images
    (this depends on cURL)])
)

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
    [path to unattend.xml windows setup file []])],
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

# --with-helper-dir
AC_ARG_WITH([helper-dir],
    [AS_HELP_STRING([--with-helper-dir=DIR],
        [top-level directory to host the helper VM
        [LOCALSTATEDIR/lib/snf-image/helper]]
    )],
    [helper_dir="$withval"],
    [helper_dir="$localstatedir/lib/snf-image/helper"])
AC_SUBST(HELPER_DIR, $helper_dir)

# --with-helper-cache-dir
AC_ARG_WITH([helper-cache-dir],
    [AS_HELP_STRING([--with-helper-cache-dir=DIR],
        [top-level directory to host the helper VM cache files
        [LOCALSTATEDIR/cache/snf-image/helper]]
    )],
    [helper_cache_dir="$withval"],
    [helper_cache_dir="$localstatedir/cache/snf-image/helper"])
AC_SUBST(HELPER_CACHE_DIR, $helper_cache_dir)

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

AC_PATH_PROG(TIMEOUT, [timeout], [], [$PATH:/usr/sbin:/sbin])
if test -z "$TIMEOUT" ; then
  AC_MSG_ERROR([timeout not found in $PATH:/usr/sbin:/sbin])
fi

AC_PATH_PROG(CURL, [curl], [], [$PATH:/usr/sbin:/sbin])
if test -z "$CURL" ; then
  AC_MSG_ERROR([curl not found in $PATH:/usr/sbin:/sbin])
fi

AC_CONFIG_FILES([
    Makefile
])

AC_OUTPUT

# vim: set sta sts=4 shiftwidth=4 sw=4 et ai :

