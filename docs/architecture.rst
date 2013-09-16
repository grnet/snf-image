Architecture
============

snf-image is split in two components: The main program running on the Ganeti
host, with full root privilege (*snf-image* previously *snf-image-host*), and a
part running inside an unprivileged, helper VM (*snf-image-helper*).

snf-image
^^^^^^^^^

This part implements the Ganeti OS interface. It extracts the Image onto the
Ganeti-provided block device, using streaming block I/O (dd with oflag=direct),
then passes control to snf-image-helper running inside a helper VM. The helper
VM is created using KVM, runs as an unprivileged user, nobody by default.

There is no restriction on the distribution running inside the helper VM, as
long as it executes the snf-image-helper component automatically upon bootup.
The snf-image-update-helper script is provided with snf-image to automate the
creation of a helper VM image based on Debian Stable, using multistrap.

The snf-image-helper component is spawned inside a specific hardware
environment:

 * The VM features a virtual floppy, containing an ext2 filesystem with all
   parameters needed for image customization.
 * The hard disk of the VM being deployed is accessible as the first virtio
   hard disk.
 * All kernel/console output is redirected to the first virtual serial console,
   and eventually finds its way into the OS definition log files that Ganeti
   maintains.
 * The helper VM is expected to output "SUCCESS" to its second serial port if
   image customization was successful inside the VM.
 * In any other case, execution of the helper VM or snf-image-helper has
   failed.
 * The helper VM is expected to shutdown automatically once it is done. Its
   execution is time-limited; if it has not terminated after a number of
   seconds, configurable via /etc/default/snf-image, it is sent a SIGTERM
   and/or a SIGKILL.

KVM is currently a dependency for snf-image, meaning it is needed to spawn the
helper VM. There is no restriction on the hypervisor used for the actual Ganeti
instances. This is not a strict requirement; KVM could be replaced by qemu,
doing full CPU virtualization without any kernel support for spawning the
helper VM.

snf-image-helper
^^^^^^^^^^^^^^^^

This part runs inside the helper VM and undertakes customization of the VM
being deployed using a number of hooks, or tasks. The tasks run in an
environment, specified by rules found in a virtual floppy, placed there by
*snf-image*. *snf-image-helper* uses runparts to run tasks found under
*/usr/lib/snf-image-helper/tasks* by default

Graphical Representation
^^^^^^^^^^^^^^^^^^^^^^^^

The architecture is presented below:

.. image:: /images/arch.png

Image Configuration Tasks
^^^^^^^^^^^^^^^^^^^^^^^^^

Configuration tasks are scripts called by snf-image-helper to accomplish
various configuration steps on the newly created instance. See below for a
description of each one of them:

**FixPartitionTable**: Enlarges the last partition in the partition table of
the instance, to consume all the available space and optionally adds a swap
partition in the end.

**FilesystemResizeUnmounted**: Extends the file system of the last partition to
cover up the whole partition. This only works for ext{2,3,4} file systems. Any
other file system type is ignored and a warning is triggered. The task will
fail if *SNF_IMAGE_DEV* environmental variable is missing.

**MountImage**: Mounts the nth partition of *SNF_IMAGE_DEV*, which is specified
by *SNF_IMAGE_PROPERTY_ROOT_PARTITION* variable under the directory specified
by *SNF_IMAGE_TARGET*. The script will fail if any of those 3 variables has a
non-sane value.

**AddSwap**: Formats the swap partion added by *FixPartitionTable* task and
adds an appropriate swap entry in the system's ``/etc/fstab``. The script will
only run if *SNF_IMAGE_PROPERTY_SWAP* is present and will fail if
*SNF_IMAGE_TARGET* in not defined.

**DeleteSSHKeys**: For linux images, this script will clear out any ssh keys
found in the image and for debian, it will recreate them too. In order to find
the ssh keys, the script looks in default locations (/etc/ssh/ssh_*_key) and
also parses ``/etc/ssh/sshd_config`` file if present. The script will fail if
*SNF_IMAGE_TARGET* is not set.

**DisableRemoteDesktopConnections**: This script temporary disables RDP
connections in windows instances by changing the value *fDenyTSConnection*
registry key. RDP connections will be enabled back during the specialize pass
of the Windows setup. The task will fail if *SNF_IMAGE_TARGET* is not defined.

**InstallUnattend**: Installs the Unattend.xml files in windows images. This is
needed by windows in order to perform an unattended setup. The
*SNF_IMAGE_TARGET* variables needs to be present for this task to run.

**SELinuxAutorelabel**: Creates *.autorelabel* file in RedHat images. This is
needed if SELinux is enabled to enforce an automatic file system relabeling at
the next boot. The only enviromental variable required by this task is
*SNF_IMAGE_TARGET*.

**AssignHostname**: Assigns or changes the hostname in a Linux or Windows
image. The task will fail if the Linux distribution is not supported. For now,
we support Debian, Redhat, Slackware, SUSE and Gentoo derived distros. The
hostname is read from *SNF_IMAGE_HOSTNAME* variable. In addition to the latter,
*SNF_IMAGE_TARGET* is also required.

**ChangePassword**: Changes the password for a list of users. For Linux systems
this is accomplished by directly altering the image's ``/etc/shadow`` file. For
Windows systems a script is injected into the VM's hard disk. This script will
be executed during the specialize pass of the Windows setup. The list of users
whose passwords will changed is determined by the *SNF_IMAGE_PROPERTY_USERS*
variable (see :ref:`image-properties`). For this task to run *SNF_IMAGE_TARGET*
and *SNF_IMAGE_PASSWORD* variables need to be present.

**FilesystemResizeMounted**: Injects a script into a Windows image file system
that will enlarge the last file system to cover up the whole partition. The
script will run during the specialize pass of the Windows setup. If the
*SNF_IMAGE_TARGET* variable is missing, the task will fail.

**EnforcePersonality**: Injects the files specified by the
*SNF_IMAGE_PROPERTY_OSFAMILY* variable into the file system. If the variable is
missing a warning is produced. The only environmental variable required is
*SNF_IMAGE_TARGET*.

**UmountImage**: Umounts the file system previously mounted by MountImage. The
only environmental variable required is *SNF_IMAGE_TARGET*.


+-------------------------------+---+--------------------------------------------+--------------------------------------------------+
|                               |   |               Dependencies                 |               Enviromental Variables [#]_        |
+          Name                 |   +------------------+-------------------------+-------------------------+------------------------+
|                               |Pr.|        Run-After |        Run-Before       |        Required         |      Optional          |
+===============================+===+==================+=========================+=========================+========================+
|FixPartitionTable              |10 |                  |FilesystemResizeUnmounted|DEV                      |                        |
+-------------------------------+---+------------------+-------------------------+-------------------------+------------------------+
|FilesystemResizeUnmounted      |20 |FixPartitionTable |MountImage               |DEV                      |                        |
+-------------------------------+---+------------------+-------------------------+-------------------------+------------------------+
|MountImage                     |30 |                  |UmountImage              |DEV                      |                        |
|                               |   |                  |                         |TARGET                   |                        |
|                               |   |                  |                         |PROPERTY_ROOT_PARTITION  |                        |
+-------------------------------+---+------------------+-------------------------+-------------------------+------------------------+
|AddSwap                        |40 |MountImage        |EnforcePersonality       |TARGET                   |PROPERTY_OSFAMILY       |
|                               |   |                  |                         |                         |PROPERTY_SWAP           |
+-------------------------------+---+------------------+-------------------------+-------------------------+------------------------+
|DeleteSSHKeys                  |40 |MountImage        |EnforcePersonality       |TARGET                   |PROPERTY_OSFAMILY       |
+-------------------------------+---+------------------+-------------------------+-------------------------+------------------------+
|DisableRemoteDesktopConnections|40 |EnforcePersonality|UmountImage              |TARGET                   |PROPERTY_OSFAMILY       |
+-------------------------------+---+------------------+-------------------------+-------------------------+------------------------+
|InstallUnattend                |40 |MountImage        |EnforcePersonality       |TARGET                   |PROPERTY_OSFAMILY       |
+-------------------------------+---+------------------+-------------------------+-------------------------+------------------------+
|SELinuxAutorelabel             |40 |MountImage        |EnforcePersonality       |TARGET                   |PROPERTY_OSFAMILY       |
+-------------------------------+---+------------------+-------------------------+-------------------------+------------------------+
|AssignHostname                 |50 |InstallUnattend   |EnforcePersonality       |TARGET                   |                        |
|                               |   |                  |                         |HOSTNAME                 |PROPERTY_OSFAMILY       |
+-------------------------------+---+------------------+-------------------------+-------------------------+------------------------+
|ChangePassword                 |50 |InstallUnattend   |EnforcePersonality       |TARGET                   |PROPERTY_USERS          |
|                               |   |                  |                         |PASSWORD                 |PROPERTY_OSFAMILY       |
+-------------------------------+---+------------------+-------------------------+-------------------------+------------------------+
|FilesystemResizeMounted        |50 |InstallUnattend   |EnforcePersonality       |TARGET                   |PROPERTY_OSFAMILY       |
+-------------------------------+---+------------------+-------------------------+-------------------------+------------------------+
|EnforcePersonality             |60 |MountImage        |UmountImage              |TARGET                   |PERSONALITY             |
|                               |   |                  |                         |                         |PROPERTY_OSFAMILY       |
+-------------------------------+---+------------------+-------------------------+-------------------------+------------------------+
|UmountImage                    |80 |MountImage        |                         |TARGET                   |                        |
+-------------------------------+---+------------------+-------------------------+-------------------------+------------------------+

.. [#] all environmental variables are prefixed with *SNF_IMAGE_*
