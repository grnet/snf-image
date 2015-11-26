Configuration
=============

The user may configure the behavior of *snf-image* by uncommenting and
overwriting the default value for some configuration parameters and the path of
some external programs in ``/etc/default/snf-image``:

.. code-block:: console

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

  # MULTISTRAP_CONFIG: Configuration file to be used with multistrap to create
  # the rootfs of the helper image.
  # MULTISTRAP_CONFIG="/etc/snf-image/multistrap.conf"

  # MULTISTRAP_APTPREFDIR: Directory where APT preference files are hosted. Those
  # files will be injected to the helper image before multistrap is called.
  # MULTISTRAP_APTPREFDIR="/etc/snf-image/apt.pref.d"

  # XEN_SCRIPTS_DIR: Directory where the Xen scripts are stored
  # XEN_SCRIPTS_DIR="/etc/xen/scripts"

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
  # STATELESS_DHCPV6_TAGS="nfdhcpd stateless_dhcpv6

  # UNATTEND: This variable overwrites the unattend.xml file used when deploying
  # a Windows image. snf-image-helper will use its own unattend.xml file if this
  # variable is empty. Please leave this empty, unless you really know what you
  # are doing.
  # UNATTEND=""

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
 * **STATELESS_DHCPV6_TAGS**: To specify which Ganeti networks support SLAAC
   and stateless DHCPv6
 * **STATEFUL_DHCPV6_TAGS**: To specify which Ganeti networks support DHCPv6
 * **UNATTEND**: To specify a custom Unattend.xml file to use on Windows
   instead of the default one

Paths of external programs
^^^^^^^^^^^^^^^^^^^^^^^^^^

In ``/etc/default/snf-image`` the user may also overwrite the path of some
external programs *snf-image* uses, or add default options to them. For
example, if the user wants to access network based images via insecure SSL
connections, he/she will need to overwrite the value of the *CURL* variable
like this: ``CURL="curl -k"``

