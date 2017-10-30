Adding cloud-init support to snf-image
======================================

How cloud-init works
^^^^^^^^^^^^^^^^^^^^

Cloud-init is a service that runs at VMs and performs VM configuration at an
early boot stage. The instructions for performing the configuration can be
collected from the configuration files and various implemented datasources.
The configuration files of cloud-init are ``/etc/cloud/cloud.cfg`` and
``/etc/cloud/cloud.cfg.d/*.cfg``. The datasources are sources for configuration
data that typically come from the user or from the IaaS service itself (e.g the
instance's name). Since different IaaS software use different mechanisms to
provide configuration data to the instances (attaching configuration disks,
using the kernel command line, using magic IPs, etc), multiple datasources are
implemented.

Why add support to snf-image
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If an image is configured to work with cloud-init, the service will destroy
some of the changes that snf-image will make. Since most distributions provide
cloud images that are configured to work with cloud-init, we would like to gain
the benefit of working with official images. Additionally, a user will be able
to further configure a VM that is created out of a cloud-init enabled image by
using cloud-init's user data mechanism.

Enabling cloud-init
^^^^^^^^^^^^^^^^^^^

In order to enable snf-image's cloud-init mode, the image should have set the
CLOUD_INIT image property.

Proposed changes
^^^^^^^^^^^^^^^^

Datasources
-----------

Since we want snf-image to be able to work stand-alone, without having to
depend on external services, the software could only make use of 2 datasources:

- NoCloud
- None

All the others expect to fetch data from an external entity (CDROM, Floppy,
serial-port, web service) [#f1]_.

"None" is the fallback datasource when no other can be selected. It is the
equivalent of an empty datasource in that it provides an empty string as
user data and an empty dictionary as metadata. We could make use of this and let
*snf-image-helper* inject all it's configuration to files under
``/etc/cloud/cloud.cfg.d/``. We could then allow the user to provide extra
configuration data by using a new OS parameter (e.g. cloud_userdata) whose
content would be injected into a file under ``/etc/cloud/cloud.cfg.d/``. The
only problem with this approach is that the user may only provide YAML user
data, which is not fully compatible with Openstack. The Nova API allows the
user to provide user data upon server creation. Those user data are available
in the OpenStack Metadata service to be consumed by cloud-init. Since we are
using *snf-image* to build a stack that exposes an OpenStack compute API, it's
highly discouraged to have an incompatibility by design.

This leaves us with the "NoCloud" option. This datasource allows us to provide
user data and metadata to the instance through a number of different ways. The
most suitable for *snf-image* is the ``/var/lib/cloud/seed/nocloud-net``
directory. The datasource will expect to find the files ``meta-data`` and
``user-data`` and optionally ``vendor-data`` as well as ``network-config``
under this directory. *snf-image* could use a dedicated task to create those
files and write the following:

.. code-block:: yaml

  datasource_list: [NoCloud]

to the cloud-init configuration. The various tasks could then perform their
configuration by concatenating the ``meta-data`` and ``vendor-data`` files or
by appending files to the cloud-init configuration directory. By definition,
the best place for *snf-image* to put the configuration would be the
``vendor-data`` file:

  Vendordata is data provided by the entity that launches an instance (for
  example, the cloud provider). This data can be used to customize the image to
  fit into the particular environment it is being run in [#f2]_.

Unfortunately, older versions of cloud-init don't play well with
``vendor-data``, which leaves us with ``meta-data`` and the files under
``/etc/cloud/cloud.cfg.d/``.

Configuration Tasks
-------------------

*snf-image* configures the VM by running a number of configuration tasks on the
hard disk of the VM. On images that support cloud-init, instead of directly
altering the needed system files, *snf-image-helper* could add cloud-init
configuration into the ``meta-data`` file as well as files under
``/etc/cloud/cloud.cfg.d/``.

The proposed changes for the configuration tasks are:

**10FixPartitionTable**: The task should be prevented from running. Cloud-init
will automatically grow the partition to consume the available space using the
``growroot`` module of cloud-initramfs-tools and ``cc_growpart`` module.

**20FilesystemResizeUnmounted**: This task should be prevented from running.
Cloud-init will automatically enlarge the file system using the ``cc_resizefs``
module.
 
**30MountImage**: No changes are needed for this task.

**35InstallUnattend**: This can stay intact or be prevented from running. It's
Windows specific task and won't do anything against a Linux image.

**40FilesystemResizeMounted**: This should be prevented from running.
Cloud-init will use ``cc_resizefs`` module to grow the file system.

**50AddSwap**: This task parses the content of the *SWAP* image property which
cames in two forms (``<partition id>:<size>`` or ``<disk letter>``) and either
creates a new swap partition or formats a whole disk to be used as swap. In 
cloud-init, the swap configuration is performed by the ``cc_mount`` module.
This module has a swap config key that can be used like this:

.. code-block:: yaml

  swap:
    filename: <file>
    size: <"auto"/size in bytes>
    maxsize: <size in bytes>

With this key we can add a swap file but not a swap partition. Since cloud-init
does the partitioning itself and using swap files is as efficient as using
partitions, in case the *SWAP* image property is defined in the first form,
it's better if we just ignore the partition id and use the swap config key to
create a swap file of the requested size instead.

In case the *SWAP* property is defined in the second form and a swap disk is
requested, we could make use of the ``mounts`` key of the ``cc_mounts`` module,
to put the appropriate entry in fstab:


.. code-block:: yaml

  mounts:
    - [ /dev/ephemeral-1, /mnt, auto, "defaults,noexec" ]
    - [ sdc, /opt/data ]
    - [ xvdh, /opt/data, "auto", "defaults,nofail", "0", "0" ]

Unfortunately, this module does not support providing non ephemeral device
names (UUID for swap) and using the standard device naming is error-prone.
Hence, for swap disks, its better if we bypass cloud-init and let snf-image
directly format the disk and put the swap entry to fstab.

**50AssignHostname**: Adding a new ``local-hostname`` key in the metadata file
should be enough to set the hostname. Alternatively, we could make use of the
``cc_update_hostname`` module which supports the following keys:

.. code-block:: yaml

  preserve_hostname: <true/false>
  fqdn: <fqdn>
  hostname: <fqdn/hostname>

We could ignore the fqdn key and use the other two.

**50ChangeMachineId**: We should probably leave this intact. Newer cloud-init
version will automatically change the machine ID to a random value as this task
does, but allowing this task to run to make sure the machine ID is always
altered even on images that user older versions of cloud-init won't harm.

**50ChangePassword**: This task will change the password and inject SSH
authorized keys to a list of users defined in the ``USERS`` image property. For
changing the password of users, we could make use of the ``cc_set_password``
module:

.. code-block:: yaml

    ssh_pwauth: <yes/no/unchanged>

    password: password1
    chpasswd:
        expire: <true/false>

    chpasswd:
        list: |
            user1:password1
            user2:RANDOM
            user3:password3
            user4:R

The ``password`` key only works for the default user and is not present in
older versions of cloud-init, which leaves us with the ``chpasswd``. Using this
key we can define the list of user-password tuples.

Injecting SSH authorized keys to a list of users is not that easy. We can make
the keys available to cloud-init by either setting the ``public-keys`` metadata
key or using the ``ssh_authorized_keys`` config key. The ``cc_ssh`` module will
inject the keys found there to the root, as well as the default user, if
defined. The preferred way to do it is through the metadata service. This way
we leave the ``ssh_authorized_keys`` config key for the user to add extra keys.

**50ConfigureNetwork**: This task may use of cloud-init's ``net`` module.
Cloud-init supports 3 network configuration formats [#f3]_:

- Network Configuration ENI (Legacy)
- Networking Config Version 1
- Networking Config Version 2

The first one is obsolete. We should probably use the version 1 of network
config which is supported by most cloud-init enabled images. This format looks
like this:

.. code-block:: yaml

  network:
    version: 1
    config:
    - type: physical
      name: eth0
      subnets:
        - type: dhcp

*snf-image* should probably implement a new networking driver:
``cloud-init.sh`` that uses the same interface as the other networking drivers
of *snf-image* (``freebsd.sh``, ``ifcfg.sh``, ``ifupdown.sh``, ``netbsd.sh``,
``nm.sh``, ``openbsd.sh.in``) and creates the networking configuration in the
version 1 format. The only problem with this is that for IPv6 networks you
cannot tell cloud-init whether slaac or slaac+dhcpv6 is to be used. This
information is available in the Router Advertisement message and should be
automatically determined by the OS upon receiving one, but many OSes do not
respect it. In order to make sure that the networking works as expected in as
many cases as possible, it's better if the cloud-init network configuration is
only used as a last resort. If snf-image detects that it knows how to configure
the instance's OS without using cloud-init, it should do so and instruct
cloud-init to omit network configuration, by appending the following to
cloud-init's configuration:

.. code-block:: yaml

  network: {config: disabled}

**50DeleteSSHKeys**: This task shall set the ``ssh_deletekeys`` configuration
key of the ``cc_ssh`` module.

**50DisableRemoteDesktopConnections**: This can stay intact or be prevented
from running. It's a Windows specific task and won't do anything against a
Linux image.

**50SELinuxAutorelabel**:  This can stay intact or be prevented from running.
It's a Windows specific task and won't do anything against a Linux image.

**60EnforcePersonality**: We could use the ``write_files`` key of the
``cc_write_files`` module to create the files that need to be injected into the
image. The problem is that if the user makes use of this key in the user-data,
the original content will be overwritten and our files will be lost. It's
better if we create a custom script under ``/var/lib/cloud/scripts/per-once``
[#f4]_ to inject the files to their destination path at first boot and leave
the ``write_files`` key for the user.

**70RunCustomTask**: This should be kept intact.

**80UmountImage**: This should be kept intact.

**81FilesystemResizeAfterUmount**: This should be prevented from running. The
``cc_resizefs`` module will do all the needed resizes.

User-defined configuration
--------------------------

The user may provide extra configuration through a new ``cloud_userdata`` OS
parameter. The content of this parameter is base64 encoded. If this parameter
is set, the ``InitializeDatasource`` configuration task will decode and then
inject its content to the ``/var/lib/cloud/seed/nocloud-net/user-data`` file.
Cloud-init will treat this as user data and will handle the rest.

Design Limitations
------------------

The users are statically defined in snf-image. The list of users whose password
will change is defined in the USERS image property, which describes the image
and not the instance. This is a problem because the user may provide user-data
that will change the list of users that cloud-init will enable or create. By
providing an new ``system_info`` list, the user may even change the name of the
default user. *snf-image* has no way to determine that the *USERS* image
property became obsolete because of provided user-data. We could solve this by
introducing a new *users* OS parameter that will overwrite (if defined) the
*USERS* image property and leave it to the user to make sure that the
instance's users *snf-image* is aware of reflect the provided cloud-init
configuration. This means that in order to use it in synnefo, we'll need add a
custom extension to the OpenStack API. OpenStack does not suffer from this
problem because it does not maintain a list of instance users to modify their
login credentials at all. Cloud-init will insert ssh authorization keys
to the root and the default users if available. Additionally, passwords are not
auto-generated by the system. It is left to the user to decide on which
instance users to change password and which passwords to use.

.. rubric:: Footnotes

.. [#f1] https://cloudinit.readthedocs.io/en/latest/topics/datasources.html#datasource-documentation

.. [#f2] https://cloudinit.readthedocs.io/en/latest/topics/vendordata.html

.. [#f3] https://cloudinit.readthedocs.io/en/latest/topics/network-config.html

.. [#f4] http://cloudinit.readthedocs.io/en/latest/topics/dir_layout.html
