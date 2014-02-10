Usage
=====

.. _sample-images:

Sample Images
^^^^^^^^^^^^^

While developing *snf-image*, we created and tested a number of images. The
following images are basic installations of some popular Linux distributions,
that have been tested with snf-image and provided here for testing purposes:


 * Debian Squeeze Base System
   [`diskdump <http://cdn.synnefo.org/debian_base-6.0-x86_64.diskdump>`_]
   [`md5sum <http://cdn.synnefo.org/debian_base-6.0-x86_64.diskdump.md5sum>`_]
   [`metadata <http://cdn.synnefo.org/debian_base-6.0-x86_64.diskdump.meta>`_]
 * Debian Wheezy Base System
   [`diskdump <http://cdn.synnefo.org/debian_base-7.0-x86_64.diskdump>`_]
   [`md5sum <http://cdn.synnefo.org/debian_base-7.0-x86_64.diskdump.md5sum>`_]
   [`metadata <http://cdn.synnefo.org/debian_base-7.0-x86_64.diskdump.meta>`_]
 * Debian Desktop
   [`diskdump <http://cdn.synnefo.org/debian_desktop-7.0-x86_64.diskdump>`_]
   [`md5sum <http://cdn.synnefo.org/debian_desktop-7.0-x86_64.diskdump.md5sum>`_]
   [`metadata <http://cdn.synnefo.org/debian_desktop-7.0-x86_64.diskdump.meta>`_]
 * CentOS 6.0
   [`diskdump <http://cdn.synnefo.org/centos-6.0-x86_64.diskdump>`_]
   [`md5sum <http://cdn.synnefo.org/centos-6.0-x86_64.diskdump.md5sum>`_]
   [`metadata <http://cdn.synnefo.org/centos-6.0-x86_64.diskdump.meta>`_]
 * Fedora Desktop 20
   [`diskdump <http://cdn.synnefo.org/fedora-20-x86_64.diskdump>`_]
   [`md5sum <http://cdn.synnefo.org/fedora-20-x86_64.diskdump.md5sum>`_]
   [`metadata <http://cdn.synnefo.org/fedora-20-x86_64.diskdump.meta>`_]
 * Ubuntu Desktop LTS 12.04
   [`diskdump <http://cdn.synnefo.org/ubuntu_desktop-12.04-x86_64.diskdump>`_]
   [`md5sum <http://cdn.synnefo.org/ubuntu_desktop-12.04-x86_64.diskdump.md5sum>`_]
   [`metadata <http://cdn.synnefo.org/ubuntu_desktop-12.04-x86_64.diskdump.meta>`_]
 * Kubuntu LTS 12.04
   [`diskdump <http://cdn.synnefo.org/kubuntu_desktop-12.04-x86_64.diskdump>`_]
   [`md5sum <http://cdn.synnefo.org/kubuntu_desktop-12.04-x86_64.diskdump.md5sum>`_]
   [`metadata <http://cdn.synnefo.org/kubuntu_desktop-12.04-x86_64.diskdump.meta>`_]
 * Ubuntu Desktop 13.10
   [`diskdump <http://cdn.synnefo.org/ubuntu_desktop-13.10-x86_64.diskdump>`_]
   [`md5sum <http://cdn.synnefo.org/ubuntu_desktop-13.10-x86_64.diskdump.md5sum>`_]
   [`metadata <http://cdn.synnefo.org/ubuntu_desktop-13.10-x86_64.diskdump.meta>`_]
 * Kubuntu 13.10
   [`diskdump <http://cdn.synnefo.org/kubuntu_desktop-13.10-x86_64.diskdump>`_]
   [`md5sum <http://cdn.synnefo.org/kubuntu_desktop-13.10-x86_64.diskdump.md5sum>`_]
   [`metadata <http://cdn.synnefo.org/kubuntu_desktop-13.10-x86_64.diskdump.meta>`_]
 * Ubuntu Server 12.04
   [`diskdump <http://cdn.synnefo.org/ubuntu_server-12.04-x86_64.diskdump>`_]
   [`md5sum <http://cdn.synnefo.org/ubuntu_server-12.04-x86_64.diskdump.md5sum>`_]
   [`metadata <http://cdn.synnefo.org/ubuntu_server-12.04-x86_64.diskdump.meta>`_]
 * OpenSUSE Desktop 13.1
   [`diskdump <http://cdn.synnefo.org/opensuse_desktop-13.1-x86_64.diskdump>`_]
   [`md5sum <http://cdn.synnefo.org/opensuse_desktop-13.1-x86_64.diskdump.md5sum>`_]
   [`metadata <http://cdn.synnefo.org/opensuse_desktop-13.1-x86_64.diskdump.meta>`_]
 * FreeBSD 9.2
   [`diskdump <http://cdn.synnefo.org/freebsd-9.2-x86_64.diskdump>`_]
   [`md5sum <http://cdn.synnefo.org/freebsd-9.2-x86_64.diskdump.md5sum>`_]
   [`metadata <http://cdn.synnefo.org/freebsd-9.2-x86_64.diskdump.meta>`_]
 * OpenBSD 5.4
   [`diskdump <http://cdn.synnefo.org/openbsd-5.4-x86_64.diskdump>`_]
   [`md5sum <http://cdn.synnefo.org/openbsd-5.4-x86_64.diskdump.md5sum>`_]
   [`metadata <http://cdn.synnefo.org/openbsd-5.4-x86_64.diskdump.meta>`_]
 * NetBSD 6.1
   [`diskdump <http://cdn.synnefo.org/netbsd-6.1-x86_64.diskdump>`_]
   [`md5sum <http://cdn.synnefo.org/netbsd-6.1-x86_64.diskdump.md5sum>`_]
   [`metadata <http://cdn.synnefo.org/netbsd-6.1-x86_64.diskdump.meta>`_]

Sample Usage
^^^^^^^^^^^^

Download an Image
+++++++++++++++++

Download a :ref:`Sample Image <sample-images>` and store it under IMAGE_DIR.
Make sure you also have its corresponding metadata file.

Spawn a diskdump image
++++++++++++++++++++++

If you want to deploy an image of type diskdump, you
need to provide the corresponding *img_properties* as described in the
:ref:`Image Format<image-format>` section. If using a diskdump found in the
:ref:`sample-images` list, use the *img_properties* described in the image's
metadata file. For example, to successfully deploy the
*debian_base-7.0-x86_64.diskdump* image file, you need to provide the following
image properties:

| OSFAMILY=linux
| ROOT_PARTITION=1
| USERS=root

Hence, the ganeti command for creating a VM from this image file would look
like this:

.. code-block:: console

  gnt-instance add -o snf-image+default \
    -O img_passwd=1Ki77y,img_format=diskdump,img_id=debian_base-7.0-x86_64,img_properties='{"OSFAMILY":"linux"\,"ROOT_PARTITION":"1"\,"USERS":"root"}' \
    -t plain --disk=0:size=10G --no-name-check --no-ip-check --no-nics my_debian_server1

If you don't want to configure the image at all and just copy it to the ganeti
provided disk, use the ``EXCLUDE_ALL_TASKS`` image property, like this:

.. code-block:: console

  gnt-instance add -o snf-image+default \
    -O img_passwd=1Ki77y,img_format=diskdump,img_id=debian_base-7.0-x86_64,img_properties='{"EXCLUDE_ALL_TASKS":"yes"}' \
    -t plain --disk=0:size=10G --no-name-check --no-ip-check --no-nics my_debian_server2

To configure a VM without first copying an image into the hard disk (e.g. if
the hard disk is a snapshot from an existing VM's hard disk) you may use the
*null* storage back-end like this:

.. code-block:: console

  gnt-instance add -o snf-image+default \
    -O img_passwd=1Ki77y,img_format=diskdump,img_id=null,img_properties='{"OSFAMILY":"linux"\,"ROOT_PARTITION":"1"\,"USERS":"root"}' \
    -t plain --disk=0:size=10G --no-name-check --no-ip-check --no-nics my_debian_server3

