Architecture
============

Overview
^^^^^^^^

*snf-image* is a Ganeti OS definition. This means that Ganeti provisions a new
disk (block device) and passes it to *snf-image*. Then, *snf-image* is
responsible to deploy an Image on that disk. If *snf-image* returns
successfully, Ganeti will then spawn a VM with that disk as its primary disk.

Thus, *snf-image* is responsible for two (2) things, which are executed in two
separate steps:

| 1. Fill the newly provisioned disk with Image data
| 2. Customize the Image accordingly

For (1), *snf-image* can fetch the Image from a number of backends, as we
describe later. For (2) *snf-image* spawns a helper VM and runs a number of
configuration tasks inside the isolated environment. Once the last task returns
successfully, the helper VM ceases and *snf-image* returns the newly configured
disk to Ganeti.

The whole procedure is configurable via OS interface parameters, that can be
passed to *snf-image* from the Ganeti command line or RAPI.

*snf-image* is split in two components: The main program running on the Ganeti
host with full root privilege (*snf-image*, previously *snf-image-host*) and a
part running inside an unprivileged helper VM (*snf-image-helper*).

We describe each part in the following sections:

snf-image
^^^^^^^^^

This part implements the Ganeti OS interface. It extracts the Image onto the
Ganeti-provided block device, using streaming block I/O (dd with oflag=direct),
then spawns a helper VM, and passes control to *snf-image-helper* running
inside that helper VM. The helper VM is created using either KVM or XEN
depending on the supported hypervisor as dictated by Ganeti. It runs as an
unprivileged user.

There is no restriction on the distribution running inside the helper VM, as
long as it executes the *snf-image-helper* component automatically upon
boot-up.  The ``snf-image-update-helper`` script is provided with *snf-image*
to automate the creation of a helper VM image based on Debian Stable, using
``multistrap``.

The *snf-image-helper* component runs inside a specific environment, which is
created and ensured by *snf-image*:

 * The VM features a virtual floppy, containing an ext2 file system with all
   parameters needed for image customization.
 * The hard disk provided by Ganeti that we want to deploy and customize is
   accessible as the first VirtIO hard disk.
 * All kernel/console output is redirected to the first virtual serial console,
   and eventually finds its way into the OS definition log files that Ganeti
   maintains.
 * The helper VM is expected to output "SUCCESS" to its second serial port if
   image customization was successful inside the VM.
 * If "SUCCESS" is not returned, *snf-image* assumes that, execution of the
   helper VM or *snf-image-helper* has failed.
 * The helper VM is expected to shutdown automatically once it is done. Its
   execution is time-limited; if it has not terminated after a number of
   seconds, configurable via ``/etc/default/snf-image``, *snf-image* sends a
   SIGTERM and/or a SIGKILL to it.

snf-image-helper
^^^^^^^^^^^^^^^^

This part runs inside the helper VM during boot-up and undertakes customization
of the target disk. It does so, by running a number of :ref:`configuration
tasks <image-configuration-tasks>`. The exact tasks that should run, are
specified by rules found in the virtual floppy, placed there by *snf-image*,
before spawning the helper VM. *snf-image-helper* uses *runparts* to run the
tasks which are found under ``/usr/lib/snf-image-helper/tasks``.

Graphical Representation
^^^^^^^^^^^^^^^^^^^^^^^^

The architecture is presented below:

.. image:: images/arch.png


.. _image-copying:

Image copying
^^^^^^^^^^^^^

As stated above, the first step (1) is to copy the image from it's original
location to the hard disk of the instance. This is performed by piping a source
back-end with a destination back-end. Source back-ends are executables that
fetch image data and write them to their standard output. In a similar manner,
destination back-ends are executables that read data from their standard input
and write them to the instance's hard disk. This design allows us to support
multiple image sources (local files, remote locations, etc.) and multiple
storage device types (local files, iSCSI devices, RBD devices, etc.). The users
may extend the functionality of snf-image by implement their own back-ends and
place them under ``/usr/share/ganeti/os/snf-image/backends/{src,dst}``.

Before the image copy is performed, the available source back-ends are probed,
one-by-one, based on their priority against the current *IMG_ID*. snf-image
will use the first one that knows how to handle the current *IMG_ID*. In the
same way, snf-image will iterate over the list of available destination
back-ends to determine which back-end knows how to handle the current
*DISK_0_DEV* or *DISK_0_URI*. After the suitable back-ends are chosen, the
image copying will be performed with a command similar to this:

.. code-block:: console

  src_backend ${IMG_ID} | dst_backend ${DISK_0_DEV}

Back-ends can either be executable files or directories. If a back-end is a
directory, it must host an executable file with the same name. This is the file
*snf-image* will call. Directories are supported in case a back-end consists of
multiple files.

Every back-end should take a positional argument (an image id
for source back-ends and a disk URI for destination back-ends) and should
support a ``-p`` option. If this option is specified, the module should output
*yes* or *no* depending on whether the given *ID* or *URI* are supported by the
back-end. Source back-ends should also support the ``-s`` options. If this is
given, the module should output the image size in bytes.

The priority of each back-end is a number between 00 to 99 stored in the file
``/etc/snf-image/backends/{src,dst}/<name>.priority``. Back-ends with higher
priority will be considered first when probing the modules to find the suitable
one. If this file is not present, the back-end's priority is set to *50*.

To disable a back-end, you can create the file
``/etc/snf-image/backends/{src,dst}/<name>.disabled``. If this file is present,
*snf-image* will completely ignore this back-end.

.. _source-backends:

Source Back-ends
""""""""""""""""

The following source back-ends are shipped with snf-image:

* **Local**:
  It is used to retrieve images that are stored on the Ganeti node that the
  image deployment takes place. All local images are expected to be found under
  a predefined directory (``/var/lib/snf-image`` by default). The user may
  alter this directory by setting the *IMAGE_DIR* variable under
  ``/etc/snf-image/backends/src/local.conf``.

* **Network**:
  It is used to retrieve images from the network using *http*, *https*, *ftp*
  or *ftps* protocols.

* **Null**:
  This is a dummy module used when no image fetching is needed

* **Pithos**:
  This is used to fetch data from pithos. To set up the pithos back-end the
  user needs to setup the ``PITHOS_BACKEND_STORAGE`` variable inside
  ``/etc/snf-image/backends/src/pithos.conf``. Possible values are ``nfs`` and
  ``rados``. If ``nfs`` is used the user needs to setup *PITHOS_DATA* variable,
  and when ``rados`` is used the user needs to setup *PITHOS_RADOS_POOL_MAPS*
  and *PITHOS_RADOS_POOL_BLOCKS* accordingly.

.. _destination-backends:

Destinatio Back-ends
""""""""""""""""""""

The following destination back-ends are currently shipped with snf-image:

* **Local**:
  This is used if the instance's disk is a local file or block device.

* **Uri**:
  This is used if the instance's disk is a Device URI qemu can deal with. This
  module will create an NBD block device using `qemu-nbd` and will use it write
  data to the instance's disk.

.. _image-configuration-tasks:

Image Configuration Tasks
^^^^^^^^^^^^^^^^^^^^^^^^^

Configuration tasks are scripts called by *snf-image-helper* inside the helper
VM to accomplish various configuration steps on the newly created instance. If
*SNF_IMAGE_PROPERTY_CLOUD_INIT* environment variable is set, the configuration
tasks will, instead of directly altering the instance's system files, inject
cloud-init configuration into the instance. See below for a description of each
one of them:

**FixPartitionTable**: Enlarges the last partition in the partition table of
the instance, to consume all the available space and optionally adds a swap
partition in the end. The task will fail if the environment variable
*SNF_IMAGE_DEV*, which specifies the device file of the instance's hard disk,
is missing. This task will not run if *SNF_IMAGE_PROPERTY_CLOUD_INIT* is set.
Cloud-init will handle the partition resizing by itself.

**FilesystemResizeUnmounted**: Extends the file system of the last partition to
cover up the whole partition. This only works for ext{2,3,4}, FFS and UFS2 file
systems. Any other file system type is ignored and a warning is triggered. The
task will fail if *SNF_IMAGE_DEV* environment variable is missing. This task
will not run if *SNF_IMAGE_PROPERTY_CLOUD_INIT* is set. Cloud-init will perform
the file system resize.

**MountImage**: Mounts the root partition of the instance, specified by the
*SNF_IMAGE_PROPERTY_ROOT_PARTITION* variable. On Linux systems after the root
fs is mounted, the instance's ``/etc/fstab`` file is examined and the rest of
the disk file systems are mounted too, in a correct order. The script will fail
if any of the environment variables *SNF_IMAGE_DEV*,
*SNF_IMAGE_PROPERTY_ROOT_PARTITION* or *SNF_IMAGE_TARGET* is unset or has a
non-sane value.

**InitializeDatasource**: This task will create the needed files for cloud-init
to use the NoCloud datasource. This task will not run unless
*SNF_IMAGE_PROPERTY_CLOUD_INIT* is set.

**InstallUnattend**: Installs the Unattend.xml files on Windows instances. This
is needed by Windows in order to perform an unattended setup. The
*SNF_IMAGE_TARGET* variables needs to be present for this task to run. This
task will not run if *SNF_IMAGE_PROPERTY_CLOUD_INIT* is set.

**FilesystemResizeMounted**: For Windows VMs this task injects a script into
the VM's file system that will enlarge the last file system to cover up the
whole partition. The script will run during the specialize pass of the Windows
setup. For Linux VMs this task is used to extend the last file system in case
its type is Btrfs or XFS, since those file systems require to be mounted in
order to resize them. If the *SNF_IMAGE_TARGET* variable is missing, the task
will fail. This task will not run if *SNF_IMAGE_PROPERTY_CLOUD_INIT* is set.
Cloud-init will perform the file system live resize.

**AddSwap**: Formats the swap partition added by *FixPartitionTable* task and
adds an appropriate swap entry in the system's ``/etc/fstab``. The script will
only run if *SNF_IMAGE_PROPERTY_SWAP* is present and will fail if
*SNF_IMAGE_TARGET* in not defined. Under cloud-init this task will enable swap
using the *cc_mounts* module.

**AssignHostname**: Assigns or changes the hostname of the instance. The task
will fail if the Linux distribution is not supported and ``/etc/hostname`` is
not present on the file system. For now, we support Debian, Red Hat, Slackware,
SUSE and Gentoo derived distributions. The hostname is read from
*SNF_IMAGE_HOSTNAME* variable. In addition to the latter, *SNF_IMAGE_TARGET* is
also required. For cloud-init, the configuration is performed by setting the
*local-hostname* key of the datasource's metadata.

**ChangeMachineId**: On Linux instances, this script will generate a new random
machine ID and will place it in ``/etc/machine-id``. For more info check
`here <https://www.freedesktop.org/software/systemd/man/machine-id.html>`_. The
task will fail if *SNF_IMAGE_TARGET* is missing.

**ChangePassword**: Changes the authentication credentials for a list of
existing users. On Linux systems this is accomplished by directly altering the
instance's ``/etc/shadow`` file. On Windows systems a script is injected into
the VM's hard disk. This script will be executed during the specialize pass of
the Windows setup. On \*BSD systems ``/etc/master.passwd`` is altered,
``/etc/spwd.db`` is removed and a script is injected into the VM's hard disk
that will recreate the aforementioned file during the first boot. The list of
users whose passwords will changed is determined by the
*SNF_IMAGE_PROPERTY_USERS* variable (see :ref:`image-properties`). On Unix
systems, if the variable *SNF_IMAGE_AUTH_KEYS* is set, the content of this
variable is injected to the authorized keys file of each user. For this task to
run *SNF_IMAGE_TARGET* and *SNF_IMAGE_PASSWD* variables need to be present. For
cloud-init, the configuration is performed using the *ssh_pwauth* and
*chpasswd* keys of the *cc_set_passwords* module, as well as, the
*public-keys* key of the datasource's meta-data.

**ConfigureNetwork**: Edit the OS's native network configuration files to
configure the instance's NICs. This works for most Linux and all the supported
\*BSD systems. In order to do this, all the NIC_* Ganeti provided environment
variables are exported to the task. The only variable required by this task is
*SNF_IMAGE_TARGET*. For this task to work correctly, the user may need to
adjust the *DHCP_TAGS* and the *\*_DHCPV6_TAGS* configuration parameters (see
:doc:`/configuration`). When working with cloud-init enabled images, this task
is performed through cloud-init using the *Network Config Version 1* format,
only if *snf-image-helper* is not aware of how to setup the network by itself.
On known distros like Debian or CentOS, snf-image-helper will prevent
cloud-init from performing the configuration.

**DeleteSSHKeys**: On Linux and \*BSD instances, this script will clear out any
ssh keys found in the instance's disk. For Debian and Ubuntu systems, the keys
are also recreated. Besides removing files that comply to the
``/etc/ssh/ssh_*_key`` pattern, the script will also parses
``/etc/ssh/sshd_config`` file for custom keys. The only variable this script
depends on is *SNF_IMAGE_TARGET*. The task will fail if *SNF_IMAGE_TARGET* is
missing. If *SNF_IMAGE_PROPERTY_CLOUD_INIT* is set, this task will just set
cloud-init's *ssh_deltekeys* configuration key.

**DisableRemoteDesktopConnections**: This script temporary disables RDP
connections on Windows instances by changing the value of *fDenyTSConnection*
registry key. RDP connections will be enabled back during the specialize pass
of the Windows setup. The task will fail if *SNF_IMAGE_TARGET* is not defined.
This task will not run if *SNF_IMAGE_PROPERTY_CLOUD_INIT* is set.

**SELinuxAutorelabel**: Creates *.autorelabel* file in Red Hat images. This is
needed if SELinux is enabled to enforce an automatic file system relabeling
during the first boot. The only environment variable required by this task is
*SNF_IMAGE_TARGET*.

**EnforcePersonality**: Injects the files specified by the
*SNF_IMAGE_PERSONALITY* variable into the file system. If the variable is
missing a warning is produced. Only *SNF_IMAGE_TARGET* is required for this
task to run. For cloud-init the file injection is performed through the
*write_files* key.

**RunCustomTask**: Run a user-defined task specified by the
*SNF_IMAGE_PROPERTY_CUSTOM_TASK* variable. If the variable is missing or empty,
a warning is produced.

**UmountImage**: Umounts the file systems previously mounted by MountImage. The
only environment variable required is *SNF_IMAGE_TARGET*.

**FilesystemResizeAfterUmount**: This is used for doing offline resize if the
file system in the last partition is NTFS. This is done after umount and not
before mounting the file system, because *ntfsresize* (which is used to perform
the actual resize) will mark the file system as dirty at the end and mounting
it afterwards is not recommended. This is done in order to force a chkdsk the
next time Windows boots. Offline NTFS resize is favored on windows-legacy and
non-windows OSes that do not support online resize. If you want to force
offline resize on newer Windows systems, the *OFFLINE_NTFSRESIZE* image
property must be defined. This task will not run if
*SNF_IMAGE_PROPERTY_CLOUD_INIT* is set.

+-------------------------------+---+-------------------------------------------------+-----------------------------------------------------+
|                               |   |               Dependencies                      |          Environment Variables [#]_                 |
+          Name                 |   +------------------+------------------------------+-------------------------+---------------------------+
|                               |Pr.|        Run-After |        Run-Before            |        Required         |   Optional                |
+===============================+===+=======================+=========================+=========================+===========================+
|FixPartitionTable              |10 |                       |FilesystemResizeUnmounted|DEV                      |                           |
+-------------------------------+---+-----------------------+-------------------------+-------------------------+---------------------------+
|FilesystemResizeUnmounted      |20 |FixPartitionTable      |MountImage               |DEV                      |RESIZE_PART                |
+-------------------------------+---+-----------------------+-------------------------+-------------------------+---------------------------+
|MountImage                     |30 |                       |UmountImage              |DEV                      |                           |
|                               |   |                       |                         |TARGET                   |                           |
|                               |   |                       |                         |PROPERTY_ROOT_PARTITION  |                           |
+-------------------------------+---+-----------------------+-------------------------+-------------------------+---------------------------+
|InitializeDatasource           |35 |MountImage             |EnforcePersonality       |TARGET                   |PROPERTY_OSFAMILY          |
|                               |   |                       |                         |                         |PROPERTY_CLOUD_INIT        |
|                               |   |                       |                         |                         |CLOUD_USERDATA             |
|                               |   |                       |                         |                         |CLOUD_INIT_DEBUG           |
+-------------------------------+---+-----------------------+-------------------------+-------------------------+---------------------------+
|InstallUnattend                |35 |MountImage             |EnforcePersonality       |TARGET                   |PROPERTY_OSFAMILY          |
+-------------------------------+---+-----------------------+-------------------------+-------------------------+---------------------------+
|FilesystemResizeMounted        |40 |InstallUnattend        |EnforcePersonality       |TARGET                   |PROPERTY_OSFAMILY          |
|                               |   |                       |                         |                         |RESIZE_PART                |
|                               |   |                       |                         |                         |PROPERTY_OFFLINE_NTFSRESIZE|
+-------------------------------+---+-----------------------+-------------------------+-------------------------+---------------------------+
|AddSwap                        |50 |MountImage             |EnforcePersonality       |TARGET                   |PROPERTY_OSFAMILY          |
|                               |   |                       |                         |                         |PROPERTY_SWAP              |
+-------------------------------+---+-----------------------+-------------------------+-------------------------+---------------------------+
|AssignHostname                 |50 |InstallUnattend        |EnforcePersonality       |TARGET                   |PROPERTY_OSFAMILY          |
|                               |   |                       |                         |HOSTNAME                 |PROPERTY_CLOUD_INIT        |
+-------------------------------+---+-----------------------+-------------------------+-------------------------+---------------------------+
|ChangeMachineId                |50 |InstallUnattend        |EnforcePersonality       |TARGET                   |PROPERTY_OSFAMILY          |
+-------------------------------+---+-----------------------+-------------------------+-------------------------+---------------------------+
|ChangePassword                 |50 |InstallUnattend        |EnforcePersonality       |TARGET                   |PROPERTY_USERS             |
|                               |   |                       |                         |                         |PROPERTY_OSFAMILY          |
|                               |   |                       |                         |                         |PASSWD                     |
|                               |   |                       |                         |                         |PASSWD_HASH                |
|                               |   |                       |                         |                         |AUTH_KEYS                  |
|                               |   |                       |                         |                         |PROPERTY_CLOUD_INIT        |
+-------------------------------+---+-----------------------+-------------------------+-------------------------+---------------------------+
|ConfigureNetwork               |50 |InstallUnattend        |EnforcePersonality       |TARGET                   |NIC_*                      |
|                               |   |                       |                         |                         |PROPERTY_CLOUD_INIT        |
+-------------------------------+---+-----------------------+-------------------------+-------------------------+---------------------------+
|DeleteSSHKeys                  |50 |MountImage             |EnforcePersonality       |TARGET                   |PROPERTY_OSFAMILY          |
+-------------------------------+---+-----------------------+-------------------------+-------------------------+---------------------------+
|EnableDatasources              |50 |FileSystemResizeMounted|EnforcePersonality       |TARGET                   |PROPERTY_OSFAMILY          |
|                               |   |                       |                         |                         |PROPERTY_CLOUD_INIT        |
|                               |   |                       |                         |                         |CLOUD_DATASOURCES          |
+-------------------------------+---+-----------------------+-------------------------+-------------------------+---------------------------+
|DisableRemoteDesktopConnections|50 |EnforcePersonality     |UmountImage              |TARGET                   |PROPERTY_OSFAMILY          |
+-------------------------------+---+-----------------------+-------------------------+-------------------------+---------------------------+
|SELinuxAutorelabel             |50 |MountImage             |EnforcePersonality       |TARGET                   |PROPERTY_OSFAMILY          |
+-------------------------------+---+-----------------------+-------------------------+-------------------------+---------------------------+
|EnforcePersonality             |60 |MountImage             |UmountImage              |TARGET                   |PERSONALITY                |
|                               |   |                       |                         |                         |PROPERTY_OSFAMILY          |
|                               |   |                       |                         |                         |PROPERTY_CLOUD_INIT        |
+-------------------------------+---+-----------------------+-------------------------+-------------------------+---------------------------+
|RunCustomTask                  |70 |MountImage             |UmountImage              |TARGET                   |PROPERTY_CUSTOM_TASK       |
+-------------------------------+---+-----------------------+-------------------------+-------------------------+---------------------------+
|UmountImage                    |80 |MountImage             |                         |TARGET                   |                           |
+-------------------------------+---+-----------------------+-------------------------+-------------------------+---------------------------+
|FilesystemResizeAfterUmount    |81 |UmountImage            |                         |DEV                      |RESIZE_PART                |
|                               |   |                       |                         |                         |PROPERTY_OSFAMILY          |
|                               |   |                       |                         |                         |PROPERTY_OFFLINE_NTFSRESIZE|
+-------------------------------+---+-----------------------+-------------------------+-------------------------+---------------------------+

.. [#] all environment variables are prefixed with *SNF_IMAGE_*
