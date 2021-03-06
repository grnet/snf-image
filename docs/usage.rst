Usage
=====

.. _sample-images:

Sample Images
^^^^^^^^^^^^^

While developing *snf-image*, we created and tested a number of images. The
following images are basic installations of some popular Linux distributions,
that have been tested with *snf-image* and provided here for testing purposes:


 * Debian Stretch Cloud-Init
   [`diskdump <https://cdn.synnefo.org/debian_cloud-9.3.4-x86_64.diskdump>`__]
   [`md5sum <https://cdn.synnefo.org/debian_cloud-9.3.4-x86_64.diskdump.md5sum>`__]
   [`metadata <https://cdn.synnefo.org/debian_cloud-9.3.4-x86_64.diskdump.meta>`__]
 * Debian Jessie Base System
   [`diskdump <https://cdn.synnefo.org/debian_base-8.0-x86_64.diskdump>`__]
   [`md5sum <https://cdn.synnefo.org/debian_base-8.0-x86_64.diskdump.md5sum>`__]
   [`metadata <https://cdn.synnefo.org/debian_base-8.0-x86_64.diskdump.meta>`__]
 * Debian Jessie Desktop
   [`diskdump <https://cdn.synnefo.org/debian_desktop-8.0-x86_64.diskdump>`__]
   [`md5sum <https://cdn.synnefo.org/debian_desktop-8.0-x86_64.diskdump.md5sum>`__]
   [`metadata <https://cdn.synnefo.org/debian_desktop-8.0-x86_64.diskdump.meta>`__]
 * CentOS 7.x
   [`diskdump <https://cdn.synnefo.org/centos-7-x86_64.diskdump>`__]
   [`md5sum <https://cdn.synnefo.org/centos-7-x86_64.diskdump.md5sum>`__]
   [`metadata <https://cdn.synnefo.org/centos-7-x86_64.diskdump.meta>`__]
 * Fedora Desktop 23
   [`diskdump <https://cdn.synnefo.org/fedora-23-x86_64.diskdump>`__]
   [`md5sum <https://cdn.synnefo.org/fedora-23-x86_64.diskdump.md5sum>`__]
   [`metadata <https://cdn.synnefo.org/fedora-23-x86_64.diskdump.meta>`__]
 * Ubuntu Mate LTS 16.04
   [`diskdump <https://cdn.synnefo.org/ubuntu_mate-16.04-x86_64.diskdump>`__]
   [`md5sum <https://cdn.synnefo.org/ubuntu_mate-16.04-x86_64.diskdump.md5sum>`__]
   [`metadata <https://cdn.synnefo.org/ubuntu_mate-16.04-x86_64.diskdump.meta>`__]
 * Ubuntu Server LTS 16.04
   [`diskdump <https://cdn.synnefo.org/ubuntu_server-16.04-x86_64.diskdump>`__]
   [`md5sum <https://cdn.synnefo.org/ubuntu_server-16.04-x86_64.diskdump.md5sum>`__]
   [`metadata <https://cdn.synnefo.org/ubuntu_server-16.04-x86_64.diskdump.meta>`__]
 * Ubuntu Desktop LTS 14.04
   [`diskdump <https://cdn.synnefo.org/ubuntu_desktop-14.04-x86_64.diskdump>`__]
   [`md5sum <https://cdn.synnefo.org/ubuntu_desktop-14.04-x86_64.diskdump.md5sum>`__]
   [`metadata <https://cdn.synnefo.org/ubuntu_desktop-14.04-x86_64.diskdump.meta>`__]
 * Ubuntu Server LTS 14.04
   [`diskdump <https://cdn.synnefo.org/ubuntu_server-14.04-x86_64.diskdump>`__]
   [`md5sum <https://cdn.synnefo.org/ubuntu_server-14.04-x86_64.diskdump.md5sum>`__]
   [`metadata <https://cdn.synnefo.org/ubuntu_server-14.04-x86_64.diskdump.meta>`__]
 * OpenSUSE Server 42.3
   [`diskdump <https://cdn.synnefo.org/opensuse_server-42.3-x86_64.diskdump>`__]
   [`md5sum <https://cdn.synnefo.org/opensuse_server-42.3-x86_64.diskdump.md5sum>`__]
   [`metadata <https://cdn.synnefo.org/opensuse_server-42.3-x86_64.diskdump.meta>`__]
 * Oracle Linux 7.x
   [`diskdump <https://cdn.synnefo.org/oraclelinux-7-x86_64.diskdump>`__]
   [`md5sum <https://cdn.synnefo.org/oraclelinux-7-x86_64.diskdump.md5sum>`__]
   [`metadata <https://cdn.synnefo.org/oraclelinux-7-x86_64.diskdump.meta>`__]
 * FreeBSD 11.1
   [`diskdump <https://cdn.synnefo.org/freebsd-11.1-x86_64.diskdump>`__]
   [`md5sum <https://cdn.synnefo.org/freebsd-11.1-x86_64.diskdump.md5sum>`__]
   [`metadata <https://cdn.synnefo.org/freebsd-11.1-x86_64.diskdump.meta>`__]
 * NetBSD 7.1
   [`diskdump <https://cdn.synnefo.org/netbsd-7.1-x86_64.diskdump>`__]
   [`md5sum <https://cdn.synnefo.org/netbsd-7.1-x86_64.diskdump.md5sum>`__]
   [`metadata <https://cdn.synnefo.org/netbsd-7.1-x86_64.diskdump.meta>`__]

Sample Usage
^^^^^^^^^^^^

Download an Image
+++++++++++++++++

Download a :ref:`Sample Image <sample-images>` and store it under *IMAGE_DIR*.
Make sure you also have its corresponding metadata file.

Spawn a diskdump image
++++++++++++++++++++++

To deploy an image of type *diskdump*, you need to provide the corresponding
**img_properties** as described in the
:ref:`Image Properties<image-properties>` section. If you want to use one of
the :ref:`sample-images`, use the **img_properties** described in the image's
metadata file. For example, to successfully deploy the
``debian_base-7.0-x86_64.diskdump`` image file, you need to provide the
following image properties:

| OSFAMILY=linux
| ROOT_PARTITION=1
| USERS=root

Hence, the Ganeti command for creating a VM from this image file would look
like this:

.. code-block:: console

  gnt-instance add -o snf-image+default \
    -O img_passwd=1Ki77y,img_format=diskdump,img_id=debian_base-7.0-x86_64,img_properties='{"OSFAMILY":"linux"\,"ROOT_PARTITION":"1"\,"USERS":"root"}' \
    -t plain --disk=0:size=10G --no-name-check --no-ip-check --no-nics my_debian_server1

If you don't want to configure the image at all and just copy it to the Ganeti
provided disk, use the *EXCLUDE_ALL_TASKS* image property, like this:

.. code-block:: console

  gnt-instance add -o snf-image+default \
    -O img_passwd=1Ki77y,img_format=diskdump,img_id=debian_base-7.0-x86_64,img_properties='{"EXCLUDE_ALL_TASKS":"yes"}' \
    -t plain --disk=0:size=10G --no-name-check --no-ip-check --no-nics my_debian_server2

To configure a VM without first copying an image into the hard disk (e.g. if
the hard disk is a snapshot from an existing VM's hard disk) you may use the
*null* storage backend like this:

.. code-block:: console

  gnt-instance add -o snf-image+default \
    -O img_passwd=1Ki77y,img_format=diskdump,img_id=null,img_properties='{"OSFAMILY":"linux"\,"ROOT_PARTITION":"1"\,"USERS":"root"}' \
    -t plain --disk=0:size=10G --no-name-check --no-ip-check --no-nics my_debian_server3

