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


.. _image-copy:

Image copying
^^^^^^^^^^^^^

For step (1), *snf-image* supports a modular interface for copying data from the
provided image to the VM's actual disk. For fetching image data, *snf-image*
supports a variety of different source backends: ``file``, ``network``,
``pithos``, and ``null``. For copying these data to the VM's disk, *snf-image*
currently supports only the ``file`` destination backend, i.e. local block
devices or files.

*snf-image* serves a different script for each backend name after the backend
type. The source backend scripts are located under
``/usr/share/ganeti/os/snf-image/backends/src/<backend type>`` while the
destination backend scripts are located under
``/usr/share/ganeti/os/snf-image/backends/dst/<backend type>``. All of them
should be executable.

The source scripts sould fetch data from the image and dump them to ``stdout``.
They should take two possitional arguments; *IMG_ID* and *IMG_FORMAT*. They
should support a ``-s`` option and if given they should return the size of the
image.

The destination scripts should read data from ``stdin`` and dump them to the
VM's disk. They should take two possitional arguments; *DISK0* and *IMG_FORMAT*.

So the whole process of image copying boils down to:

#. Parse *IMG_ID* and get the source backend type.
#. Parse *DISK_0_PATH* or *DISK_0_URI* and get the destination backend type.
#. Check if the corresponding scripts exist.
#. Invoke the source script with the -s option to get the image size.
#. Create a process chain of the source script, the monitor script,
   and the destination script "connected" with pipes.

The above steps will eventually fetch data from the image, pass them
to the monitor, and finally dump them to the VM's disk.

.. _source-backends:

Source Backends
"""""""""""""""

*snf-image* is capable of fetching images that are stored in a variety of
different backends. It decides which backend to use based on the *IMG_ID*
:ref:`parameter <image-id>`. Currently *snf-image* supports the following
backends:

 * **File backend**:
   The local backend is used to retrieve images that are stored on the Ganeti
   node that the image deployment takes place. All local images are expected to
   be found under a predefined image directory. By default */var/lib/snf-image*
   is used, but the user may change this by overwriting the value of the
   *IMAGE_DIR* variable under ``/etc/default/snf-image``.

 * **Network backend**:
   The network backend is used to retrieve images that are accessible from the
   network. snf-image can fetch images via *http:*, *https:*, *ftp:* or
   *ftps:*, using `cURL <http://curl.haxx.se/>`_.

 * **Pithos backend**:
   *snf-image* contains a special command-line tool (*pithcat*) for retrieving
   images residing on a Pithos installation. To set up *snf-image*'s Pithos
   backend the user needs to setup the ``PITHOS_BACKEND_STORAGE`` variable
   inside ``/etc/default/snf-image``.
   Possible values are ``nfs`` and ``rados``. If ``nfs`` is used the user needs
   to setup *PITHOS_DATA* variable, and when ``rados`` is used the user needs
   to setup *PITHOS_RADOS_POOL_MAPS* and *PITHOS_RADOS_POOL_BLOCKS*
   accordingly.

 * **Null backend**:
   If the null backend is selected, no image copying is performed. This
   actually is meant for bypassing step (1) altogether. This is useful, if the
   disk provisioned by Ganeti already contains an OS installation before
   *snf-image* is executed (for example if the disk was created as a clone of
   an existing VM's hard disk).

.. _destination-backends:

Destination Backends
""""""""""""""""""""

Since Ganeti supports userspace access to disks (e.g. via the RBD
and the ExtStorage disk template) the existence of a local block device should
not be taken for granted, and thus a simple ``dd`` might not work. For example,
in case of RADOS without having the volume locally mapped this would not work.
Additionally in case of Archipelago, if we choose to go only with QEMU userspace
support (without using blktap to create a local block device) this would not
work either.

To get the destination backend type, *snf-image* first parses the *DISK_0_PATH*
as exported by Ganeti. If this is neither a block device nor a file, it
parsed *DISK_0_URI*. If found, the expected format is::

  <backend type>:<some identifier>

For example, in case of RADOS, the *DISK_0_URI* would be something like::

  rbd:<rbd pool>/<rbd name>

or, in case of Archipelago, it would be::

  archipelago:<volume name>

Currently *snf-image* supports the following backends:

 * **File backend**:
   This backend supports instance disks that are local files or block devices.
   The image data will get dumped to the VM's disk using a simple ``dd`` reading
   from stdin. In case of ntfsdump or extdump image types, the script
   will losetup the disk, create partitions, install a new MBR then copy
   the filesystem on the first partition.


.. _image-configuration-tasks:

Image Configuration Tasks
^^^^^^^^^^^^^^^^^^^^^^^^^

Configuration tasks are scripts called by *snf-image-helper* inside the helper
VM to accomplish various configuration steps on the newly created instance. See
below for a description of each one of them:

**FixPartitionTable**: Enlarges the last partition in the partition table of
the instance, to consume all the available space and optionally adds a swap
partition in the end. The task will fail if the environment variable
*SNF_IMAGE_DEV*, which specifies the device file of the instance's hard disk,
is missing.

**FilesystemResizeUnmounted**: Extends the file system of the last partition to
cover up the whole partition. This only works for ext{2,3,4}, FFS and UFS2 file
systems. Any other file system type is ignored and a warning is triggered. The
task will fail if *SNF_IMAGE_DEV* environment variable is missing.

**MountImage**: Mounts the root partition of the instance, specified by the
*SNF_IMAGE_PROPERTY_ROOT_PARTITION* variable. On Linux systems after the root
fs is mounted, the instance's ``/etc/fstab`` file is examined and the rest of
the disk file systems are mounted too, in a correct order. The script will fail
if any of the environment variables *SNF_IMAGE_DEV*,
*SNF_IMAGE_PROPERTY_ROOT_PARTITION* or *SNF_IMAGE_TARGET* is unset or has a
non-sane value.

**InstallUnattend**: Installs the Unattend.xml files on Windows instances. This
is needed by Windows in order to perform an unattended setup. The
*SNF_IMAGE_TARGET* variables needs to be present for this task to run.

**FilesystemResizeMounted**: For Windows VMs this task injects a script into
the VM's file system that will enlarge the last file system to cover up the
whole partition. The script will run during the specialize pass of the Windows
setup. For Linux VMs this task is used to extend the last file system in case
its type is Btrfs or XFS, since those file systems require to be mounted in
order to resize them. If the *SNF_IMAGE_TARGET* variable is missing, the task
will fail.

**AddSwap**: Formats the swap partition added by *FixPartitionTable* task and
adds an appropriate swap entry in the system's ``/etc/fstab``. The script will
only run if *SNF_IMAGE_PROPERTY_SWAP* is present and will fail if
*SNF_IMAGE_TARGET* in not defined.

**AssignHostname**: Assigns or changes the hostname of the instance. The task
will fail if the Linux distribution is not supported and ``/etc/hostname`` is
not present on the file system. For now, we support Debian, Red Hat, Slackware,
SUSE and Gentoo derived distributions. The hostname is read from
*SNF_IMAGE_HOSTNAME* variable. In addition to the latter, *SNF_IMAGE_TARGET* is
also required.

**ChangeMachineId**: On Linux instances, this script will generate a new random
machine ID and will place it in ``/etc/machine-id``. For more info check
`here <https://www.freedesktop.org/software/systemd/man/machine-id.html>`_. The
task will fail if *SNF_IMAGE_TARGET* is missing.

**ChangePassword**: Changes the password for a list of existing users. On Linux 
systems this is accomplished by directly altering the instance's
``/etc/shadow`` file. On Windows systems a script is injected into the VM's
hard disk. This script will be executed during the specialize pass of the
Windows setup. On \*BSD systems ``/etc/master.passwd`` is altered,
``/etc/spwd.db`` is removed and a script is injected into the VM's hard disk
that will recreate the aforementioned file during the first boot. The list of
users whose passwords will changed is determined by the
*SNF_IMAGE_PROPERTY_USERS* variable (see :ref:`image-properties`). For this
task to run *SNF_IMAGE_TARGET* and *SNF_IMAGE_PASSWD* variables need to be
present.

**ConfigureNetwork**: Edit the OS's native network configuration files to
configure the instance's NICs. This works for most Linux and all the supported
\*BSD systems. In order to do this, all the NIC_* Ganeti provided environment
variables are exported to the task. The only variable required by this task is
*SNF_IMAGE_TARGET*. For this task to work correctly, the user may need to
adjust the *DHCP_TAGS* and the *\*_DHCPV6_TAGS* configuration parameters (see
:doc:`/configuration`).

**DeleteSSHKeys**: On Linux and \*BSD instances, this script will clear out any
ssh keys found in the instance's disk. For Debian and Ubuntu systems, the keys
are also recreated. Besides removing files that comply to the
``/etc/ssh/ssh_*_key`` pattern, the script will also parses
``/etc/ssh/sshd_config`` file for custom keys. The only variable this script
depends on is *SNF_IMAGE_TARGET*.

**DisableRemoteDesktopConnections**: This script temporary disables RDP
connections on Windows instances by changing the value of *fDenyTSConnection*
registry key. RDP connections will be enabled back during the specialize pass
of the Windows setup. The task will fail if *SNF_IMAGE_TARGET* is not defined.

**SELinuxAutorelabel**: Creates *.autorelabel* file in Red Hat images. This is
needed if SELinux is enabled to enforce an automatic file system relabeling
during the first boot. The only environment variable required by this task is
*SNF_IMAGE_TARGET*.

**EnforcePersonality**: Injects the files specified by the
*SNF_IMAGE_PERSONALITY* variable into the file system. If the variable is
missing a warning is produced. Only *SNF_IMAGE_TARGET* is required for this
task to run.

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
property must be defined.

+-------------------------------+---+--------------------------------------------+-----------------------------------------------------+
|                               |   |               Dependencies                 |          Environment Variables [#]_                 |
+          Name                 |   +------------------+-------------------------+-------------------------+---------------------------+
|                               |Pr.|        Run-After |        Run-Before       |        Required         |   Optional                |
+===============================+===+==================+=========================+=========================+===========================+
|FixPartitionTable              |10 |                  |FilesystemResizeUnmounted|DEV                      |                           |
+-------------------------------+---+------------------+-------------------------+-------------------------+---------------------------+
|FilesystemResizeUnmounted      |20 |FixPartitionTable |MountImage               |DEV                      |RESIZE_PART                |
+-------------------------------+---+------------------+-------------------------+-------------------------+---------------------------+
|MountImage                     |30 |                  |UmountImage              |DEV                      |                           |
|                               |   |                  |                         |TARGET                   |                           |
|                               |   |                  |                         |PROPERTY_ROOT_PARTITION  |                           |
+-------------------------------+---+------------------+-------------------------+-------------------------+---------------------------+
|InstallUnattend                |35 |MountImage        |EnforcePersonality       |TARGET                   |PROPERTY_OSFAMILY          |
+-------------------------------+---+------------------+-------------------------+-------------------------+---------------------------+
|FilesystemResizeMounted        |40 |InstallUnattend   |EnforcePersonality       |TARGET                   |PROPERTY_OSFAMILY          |
|                               |   |                  |                         |                         |RESIZE_PART                |
|                               |   |                  |                         |                         |PROPERTY_OFFLINE_NTFSRESIZE|
+-------------------------------+---+------------------+-------------------------+-------------------------+---------------------------+
|AddSwap                        |50 |MountImage        |EnforcePersonality       |TARGET                   |PROPERTY_OSFAMILY          |
|                               |   |                  |                         |                         |PROPERTY_SWAP              |
+-------------------------------+---+------------------+-------------------------+-------------------------+---------------------------+
|AssignHostname                 |50 |InstallUnattend   |EnforcePersonality       |TARGET                   |                           |
|                               |   |                  |                         |HOSTNAME                 |PROPERTY_OSFAMILY          |
+-------------------------------+---+------------------+-------------------------+-------------------------+---------------------------+
|ChangeMachineId                |50 |InstallUnattend   |EnforcePersonality       |TARGET                   |PROPERTY_OSFAMILY          |
+-------------------------------+---+------------------+-------------------------+-------------------------+---------------------------+
|ChangePassword                 |50 |InstallUnattend   |EnforcePersonality       |TARGET                   |PROPERTY_USERS             |
|                               |   |                  |                         |                         |PROPERTY_OSFAMILY          |
|                               |   |                  |                         |                         |PASSWD                     |
+-------------------------------+---+------------------+-------------------------+-------------------------+---------------------------+
|ConfigureNetwork               |50 |InstallUnattend   |EnforcePersonality       |TARGET                   |NIC_*                      |
+-------------------------------+---+------------------+-------------------------+-------------------------+---------------------------+
|DeleteSSHKeys                  |50 |MountImage        |EnforcePersonality       |TARGET                   |PROPERTY_OSFAMILY          |
+-------------------------------+---+------------------+-------------------------+-------------------------+---------------------------+
|DisableRemoteDesktopConnections|50 |EnforcePersonality|UmountImage              |TARGET                   |PROPERTY_OSFAMILY          |
+-------------------------------+---+------------------+-------------------------+-------------------------+---------------------------+
|SELinuxAutorelabel             |50 |MountImage        |EnforcePersonality       |TARGET                   |PROPERTY_OSFAMILY          |
+-------------------------------+---+------------------+-------------------------+-------------------------+---------------------------+
|EnforcePersonality             |60 |MountImage        |UmountImage              |TARGET                   |PERSONALITY                |
|                               |   |                  |                         |                         |PROPERTY_OSFAMILY          |
+-------------------------------+---+------------------+-------------------------+-------------------------+---------------------------+
|RunCustomTask                  |70 |MountImage        |UmountImage              |TARGET                   |PROPERTY_CUSTOM_TASK       |
+-------------------------------+---+------------------+-------------------------+-------------------------+---------------------------+
|UmountImage                    |80 |MountImage        |                         |TARGET                   |                           |
+-------------------------------+---+------------------+-------------------------+-------------------------+---------------------------+
|FilesystemResizeAfterUmount    |81 |UmountImage       |                         |DEV                      |RESIZE_PART                |
|                               |   |                  |                         |                         |PROPERTY_OSFAMILY          |
|                               |   |                  |                         |                         |PROPERTY_OFFLINE_NTFSRESIZE|
+-------------------------------+---+------------------+-------------------------+-------------------------+---------------------------+

.. [#] all environment variables are prefixed with *SNF_IMAGE_*
