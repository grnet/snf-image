Configuration
=============

The user may configure the behavior of *snf-image* by uncommenting and
overwriting the default value for some configuration parameters and the path of
some external programs in ``/etc/default/snf-image``:

.. code::

  # snf-image defaults file

  # IMAGE_DIR: directory location for disk images
  # IMAGE_DIR="/var/lib/snf-image"

  # IMAGE_DEBUG: turn on debugging output for the scripts
  # IMAGE_DEBUG=no

  # VERSION_CHECK: Check if snf-image and snf-image-helper have the same version.
  # This is useful if snf-image is installed as Debian package and not from
  # source.
  # VERSION_CHECK="yes"

  # HELPER_DIR: Directory hosting the helper files
  # HELPER_DIR="/var/lib/snf-image/helper/"

  # HELPER_TIMEOUT: Soft and hard timeout limits for helper instance. The helper
  # instance will be terminated after a given time if it hasn't exited by itself.
  # A TERM signal will be send if the instance is running after a
  # HELPER_SOFT_TIMEOUT interval. A KILL signal will be sent, if the instance is
  # still running after a HELPER_HARD_TIMEOUT interval since the initial signal
  # was sent. The timeout values are integer numbers with an optional suffix: `s'
  # for seconds (the default), `m' for minutes, `h' for hours or `d' for days.
  # HELPER_SOFT_TIMEOUT="120"
  # HELPER_HARD_TIMEOUT="5"

  # HELPER_USER: For security reasons, it is recommended that the helper VM
  # runs as an unprivileged user. KVM drops root privileges and runs as
  # HELPER_USER immediately before starting execution of the helper VM.
  # HELPER_USER="nobody"

  # HELPER_MEMORY: Virtual RAM size in megabytes to be given to the helper VM.
  # HELPER_MEMORY="512"

  # HELPER_DEBUG: When enabled, the helper VM will drop to a root shell
  # whenever a task fails. This allows the administrator or a developer
  # to examine its internal state for debugging purposes.
  # To access the shell, use a program like 'minicom' to connect to /dev/pts/X on
  # the host, where /dev/pts/X is the name of the device reported in the Ganeti
  # OS installation logs for helper's 3rd serial port, e.g.,
  # "char device redirected to /dev/pts/9 (label serial3)".
  # This feature is KVM-specific for the time being.
  # For HELPER_DEBUG to be useful, you also need to set HELPER_SOFT_TIMEOUT
  # to a much higher value.
  # WARNING: DO NOT ENABLE THIS FEATURE IN PRODUCTION. Every failure to deploy
  # an Image will cause the helper VM to hang.
  # HELPER_DEBUG="no"

  # MULTISTRAP_CONFIG: Configuration file to be used with multistrap to create
  # the rootfs of the helper image.
  # MULTISTRAP_CONFIG="/etc/snf-image/multistrap.conf"

  # MULTISTRAP_APTPREFDIR: Directory where APT preference files are hosted. Those
  # files will be injected to the helper image before multistrap is called.
  # MULTISTRAP_APTPREFDIR="/etc/snf-image/apt.pref.d"

  # XEN_SCRIPTS_DIR: Directory where the Xen scripts are stored
  # XEN_SCRIPTS_DIR="/etc/xen/scripts"

  # XEN_CMD: This variable specifies the Xen CLI tool snf-image should use. This
  # depends on the XEN version and configuration and should probably coincide
  # with the Ganeti's xen_cmd hypervisor parameter for xen-hvm or xen-pvm. Right
  # now the supported ones are 'xm' and 'xl'.
  # XEN_CMD="xl"

  # PITHOS_DB: Pithos database in SQLAlchemy format
  # PITHOS_DB="sqlite://///var/lib/pithos/backend.db"

  # PITHOS_BACKEND_STORAGE: Select Pithos backend storage. Possible values are
  # 'nfs' and 'rados'. According to the value you select, you need to set the
  # corresponding variables that follow.
  # If you select 'nfs' that's 'PITHOS_DATA'. If you select 'rados' then you need
  # to set all the "*_RADOS_*" ones.
  # PITHOS_BACKEND_STORAGE="nfs"

  # PITHOS_DATA: Directory where Pithos data are hosted
  # PITHOS_DATA="//var/lib/pithos/data"

  # PITHOS_RADOS_CEPH_CONF: RADOS configuration file
  # PITHOS_RADOS_CEPH_CONF="/etc/ceph/ceph.conf"

  # PITHOS_RADOS_POOL_MAPS: RADOS pool for storing Pithos maps
  # PITHOS_RADOS_POOL_MAPS="maps"

  # PITHOS_RADOS_POOL_BLOCKS: RADOS pool for storing Pithos blocks
  # PITHOS_RADOS_POOL_BLOCKS="blocks"

  # PITHOS_ARCHIPELAGO_CONF: Archipelago configuration file
  # PITHOS_ARCHIPELAGO_CONF="/etc/archipelago/archipelago.conf"

  # PITHCAT_UMASK: If set, it will change the file mode mask of the pithcat
  # process to the specified one.
  # PITHCAT_UMASK=<not set>

  # PROGRESS_MONITOR: External program that monitors the progress of the image
  # deployment. The snf-image monitor messages will be redirected to the standard
  # input of this program.
  # PROGRESS_MONITOR=""

  # DHCP_TAGS: Space separated list of Ganeti network tags. snf-image will
  # configure a VM's NIC to use DHCP if the card is expected to have an IPv4
  # address and any of those tags is present in the card's NETWORK_TAGS variable.
  # DHCP_TAGS="auto dhcp nfdhcpd"

  # STATEFUL_DHCPV6_TAGS: Space separated list of Ganeti network tags. snf-image
  # will configure a VM's NIC to use DHCPv6 if the card is expected to have an
  # IPv6 address and any of those tags is present in the card's NETWORK_TAGS
  # variable.
  # STATEFUL_DHCPV6_TAGS="dhcpv6 stateful_dhcpv6"

  # STATELESS_DHCPV6_TAGS: Space separated list of Ganeti network tags. snf-image
  # will configure a VM's NIC to perform SLAAC and Stateless DHCPv6 if the card
  # is expected to have an IPv6 address and any of those tags is present in the
  # card's NETWORK_TAGS variable.
  # STATELESS_DHCPV6_TAGS="nfdhcpd stateless_dhcpv6"

  # DEFAULT_NIC_CONFIG: This option defines the network configuration to be
  # performed if there is a default NIC attached to the instance with no further
  # information associated with it. This will happen if the user creates an
  # instance and does not define any of the --net and --no-nics input arguments.
  # In this case Ganeti will create a NIC with a random MAC and set up according
  # to the cluster level NIC parameters. The user may want to leave this NIC
  # unconfigured (by leaving this option empty), perform "dhcp" or use one of the
  # various IPv6 auto configuration methods. The supported IPv6 methods are:
  # "dhcpv6" (Stateful DHCPv6), "slaac_dhcp" (Stateless DHCPv6) and "slaac"
  # (Stateless Autoconfiguration). IPv4 and IPv6 configuration methods can be
  # defined in conjunction using the plus (`+') sign. IPv4 must precede (e.g.:
  # "dhcp+slaac_dhcp").
  # DEFAULT_NIC_CONFIG="dhcp"

  # UNATTEND: This variable overwrites the unattend.xml file used when deploying
  # a Windows image. snf-image-helper will use its own unattend.xml file if this
  # variable is empty.
  # WARNING: This variable is DEPRECATED. If you need to define an answer file
  # different that the one shipped with snf-image, which is very likely, put it
  # inside the image or use the os_answer_file OS parameter.
  # UNATTEND=""

  # WINDOWS_TIMEZONE: This variable is used to specify the time zone when
  # deploying a Windows image. This will only work if you are using snf-image's
  # default OS answer file. If the Windows image already contains an answer file
  # or the os_answer_file OS parameter is used to define one, this variable will
  # be completely ignored. For a list of available time zones, check here:
  # https://msdn.microsoft.com/en-us/library/ms912391%28v=winembedded.11%29.aspx
  # WINDOWS_TIMEZONE="GMT Standard Time"

  # Paths for needed programs. Uncomment and change the variables below if you
  # don't want to use the default one.
  # MD5SUM="md5sum"
  # KVM="kvm"
  # LOSETUP="losetup"
  # KPARTX="kpartx"
  # SFDISK="sfdisk"
  # INSTALL_MBR="install-mbr"
  # TIMEOUT="timeout"
  # CURL="curl"
  # TAR="tar"

.. _configuration-parameters:

Configuration parameters
^^^^^^^^^^^^^^^^^^^^^^^^

The most common configuration parameters the user may need to overwrite are:

 * **IMAGE_DIR**: To specify the directory where the local images are hosted
 * **HELPER_SOFT_TIMEOUT**: To increase the allowed deployment time
 * **PITHOS_DB**: To specify the Pithos database and credentials, in case the
   user is accessing Pithos-hosted images
 * **PITHOS_DATA**: To specify the directory where the Pithos data blocks are
   hosted, in case the user is accessing Pithos-hosted images
 * **PROGRESS_MONITOR**: To specify an executable that will handle the
   monitoring messages exported by *snf-image*
 * **DHCP_TAGS**: To specify which Ganeti networks support DHCP
 * **DEFAULT_NIC_CONFIG**: To specify a configuration method for the default
   NIC Ganeti will attach on instances that were created without using the
   *--net* or *--no-nics* input arguments.
 * **STATELESS_DHCPV6_TAGS**: To specify which Ganeti networks support SLAAC
   and stateless DHCPv6
 * **STATEFUL_DHCPV6_TAGS**: To specify which Ganeti networks support DHCPv6
 * **WINDOWS_TIMEZONE**: To specify a time zone to use when deploying Windows
   images that do not host an Unattend.xml file and depend on the one provided
   by *snf-image*.

Paths of external programs
^^^^^^^^^^^^^^^^^^^^^^^^^^

In ``/etc/default/snf-image`` the user may also overwrite the path of some
external programs *snf-image* uses, or add default options to them. For
example, if the user wants to access network based images via insecure SSL
connections, he/she will need to overwrite the value of the *CURL* variable
like this: ``CURL="curl -k"``

