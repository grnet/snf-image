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
 * Fedora Desktop 18
   [`diskdump <http://cdn.synnefo.org/fedora-18-x86_64.diskdump>`_]
   [`md5sum <http://cdn.synnefo.org/fedora-18-x86_64.diskdump.md5sum>`_]
   [`metadata <http://cdn.synnefo.org/fedora-18-x86_64.diskdump.meta>`_]
 * Ubuntu Desktop LTS 12.04
   [`diskdump <http://cdn.synnefo.org/ubuntu_desktop-12.04-x86_64.diskdump>`_]
   [`md5sum <http://cdn.synnefo.org/ubuntu_desktop-12.04-x86_64.diskdump.md5sum>`_]
   [`metadata <http://cdn.synnefo.org/ubuntu_desktop-12.04-x86_64.diskdump.meta>`_]
 * Kubuntu LTS 12.04
   [`diskdump <http://cdn.synnefo.org/kubuntu_desktop-12.04-x86_64.diskdump>`_]
   [`md5sum <http://cdn.synnefo.org/kubuntu_desktop-12.04-x86_64.diskdump.md5sum>`_]
   [`metadata <http://cdn.synnefo.org/kubuntu_desktop-12.04-x86_64.diskdump.meta>`_]
 * Ubuntu Desktop 13.04
   [`diskdump <http://cdn.synnefo.org/ubuntu_desktop-13.04-x86_64.diskdump>`_]
   [`md5sum <http://cdn.synnefo.org/ubuntu_desktop-13.04-x86_64.diskdump.md5sum>`_]
   [`metadata <http://cdn.synnefo.org/ubuntu_desktop-13.04-x86_64.diskdump.meta>`_]
 * Kubuntu 13.04
   [`diskdump <http://cdn.synnefo.org/kubuntu_desktop-13.04-x86_64.diskdump>`_]
   [`md5sum <http://cdn.synnefo.org/kubuntu_desktop-13.04-x86_64.diskdump.md5sum>`_]
   [`metadata <http://cdn.synnefo.org/kubuntu_desktop-13.04-x86_64.diskdump.meta>`_]
 * Ubuntu Server 12.04
   [`diskdump <http://cdn.synnefo.org/ubuntu_server-12.04-x86_64.diskdump>`_]
   [`md5sum <http://cdn.synnefo.org/ubuntu_server-12.04-x86_64.diskdump.md5sum>`_]
   [`metadata <http://cdn.synnefo.org/ubuntu_server-12.04-x86_64.diskdump.meta>`_]
 * OpenSUSE Desktop 12.3
   [`diskdump <http://cdn.synnefo.org/opensuse_desktop-12.3-x86_64.diskdump>`_]
   [`md5sum <http://cdn.synnefo.org/opensuse_desktop-12.3-x86_64.diskdump.md5sum>`_]
   [`metadata <http://cdn.synnefo.org/opensuse_desktop-12.3-x86_64.diskdump.meta>`_]
 * FreeBSD 9.1
   [`diskdump <http://cdn.synnefo.org/freebsd-9.1-x86_64.diskdump>`_]
   [`md5sum <http://cdn.synnefo.org/freebsd-9.1-x86_64.diskdump.md5sum>`_]
   [`metadata <http://cdn.synnefo.org/freebsd-9.1-x86_64.diskdump.meta>`_]

Sample Usage
^^^^^^^^^^^^

Download an Image
+++++++++++++++++

Download a :ref:`Sample Image <sample-images>` and store it under IMAGE_DIR.
Make sure you also have its corresponding metadata file.

Spawn a diskdump image
++++++++++++++++++++++

If you want to deploy an image of type diskdump, you need to provide the
corresponding *img_properties* as described in the
:ref:`Image Format<image-format>` section. If using a diskdump found in the
:ref:`sample-images` list, use the *img_properties* described in the image's
metadata file. For example:

``gnt-instance add -o snf-image+default --os-parameters img_passwd=SamplePassw0rd,img_format=diskdump,img_id=debian_base-6.0-7-x86_64,img_properties='{"OSFAMILY":"linux"\,"ROOT_PARTITION":"1"}' -t plain --disk=0:size=10G --no-name-check --no-ip-check --no-nics test1``

