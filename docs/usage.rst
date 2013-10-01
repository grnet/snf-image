Usage
=====

Ganeti OS Interface
^^^^^^^^^^^^^^^^^^^

*snf-image* requires ganeti-os-interface v20 to operate and it introduces the
following OS Parameters:

 * **img_format** (required if *config_url* is missing): the image format type
   (:ref:`details <image-format>`)
 * **img_id** (required if *config_url* is missing): the URI used to identify
   the image (:ref:`details <image-id>`)
 * **img_passwd** (required if *config_url* is missing): the password to be
   injected to the image
 * **img_properties** (optional): additional image properties used to customize
   the image (:ref:`details <image-properties>`)
 * **img_personality** (optional): files to be injected into the image
   filesystem (:ref:`details <image-personality>`)
 * **config_url** (optional): the url to download configuration data from

.. _image-format:

Image Format
^^^^^^^^^^^^

snf-image supports 3 different types of image formats:

 * **diskdump** (recommended): a raw dump of a disk
 * **extdump**: a raw dump of an ext{2,3,4} file system
 * **ntfsdump**: a raw dump of an NTFS file system

These are also the only valid values for the **img_format** OS parameter.
The **diskdump** type is the newest and recommended type. Thus, all sample
images we provide are of this type. For more details about the internals of
image formats please see the :ref:`corresponding advanced section
<image-format-advanced>`.

.. _image-id:

Image IDs & Storage back-ends
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

*snf-image* capable of deploying images that are stored in a variety of
different back-ends. The back-end to be used is determined by the value of the
*img_id* OS parameter. The following back-ends are supported:

 * **Local back-end**:
   The local back-end is used to retrieve images that are stored in the ganeti
   node that the image deployment takes place. The local back-end is used if
   the value of the *img_id* ganeti OS parameter is either prefixed with
   *file://* or is not prefixed at all. All local images are expected to be
   found under a predifined image directory. By default */var/lib/snf-image* is
   used, but the user may change this by overwriting the value of the
   *IMAGE_DIR* variable under ``/etc/default/snf-image``. The name of the image
   file is created by adding the image type extension in the end of the
   *img_id*. For example if the *img_id* is *file://slackware* and the image
   type is *diskdump*, snf-image will expect to find an image file under the
   following path: ``/usr/lib/snf-image/slackware.diskdump``

 * **Network back-end**:
   The network back-end is used to retrieve images that are accessible from the
   network. If the *imd_id* starts with *http:*, *https:*, *ftp:* or *ftps:*,
   snf-image will treat the *img_id* as a remote URL and will try to fetch the
   image using `cURL <http://curl.haxx.se/>`_.

 * **Pithos back-end**:
   If an *img_id* is prefixed with *pithos:* or *pithosmap:* the image is
   considered to be pithos back-ended. *snf-image* contains a special
   command-line tool (*pithcat*) for retrieving this kind of images. For
   *pithosmap:* images, the user needs to have set a valid value for the
   *PITHOS_DATA* variable. For *pithos:* images, in addition to PITHOS_DATA,
   the PITHOS_DB variable needs to contain a valid value too.
   ``/etc/default/snf-image`` may be used to set both values.

 * **Null back-end**:
   The null back-end is used if the *img_id* value is *null*. In this case no
   image copying is performed. This is usefull if the hard disk already
   contains an OS installation before *snf-image* is executed (for example if
   the hard disk is a snapshot of an existing VM's hard disk).

.. _image-properties:

Image Properties
^^^^^^^^^^^^^^^^

In order for *snf-image* to be able to properly configure an image, it may make
use of a set of image properties. Those image properties are passed to
*snf-image* by Ganeti through the *img_poroperties* OS parameter (see Ganeti OS
Interface). The name of all image properties is case-insensitive. For the
diskdump format some properties are mandatory. For {ext,ntfs}dump formats all
image properties are optional.

A list of mandatory and optional properties follows:

Mandatory properties (diskdump only)
++++++++++++++++++++++++++++++++++++

 * **OSFAMILY={linux,windows}**
   This specifies whether the image is a Linux or a Windows Image.
   {ext,ntfs}dump formats are self descriptive regarding this property.
 * **ROOT_PARTITION=n**
   This specifies the partition number of the root partition. As mentioned
   earlier, for now, only primary partitions are supported. This property is
   trivial for {ext,ntfs}dump formats (they only host one partition).

Optional properties
+++++++++++++++++++

 * **USERS="username1 username2...."**
   This is a space-seperated list of users, whose password will be reset by
   *snf-image*. The use of this property is optional, but highly recommended.
   For now, if this property is missing, the users are chosen according to a
   set of rules, but those rules may change or even be dropped in the future.
   The rules we currently use are listed below:

     * For Windows images, the *Administrator*'s password is reset.
     * For Linux and FreeBSD images, the *root* password is reset.

 * **EXCLUDE_ALL_TASKS=yes**
   If this property is defined with a value other than null, then during the
   deployment, the image will not be configured at all. This is really handy
   because it gives the ability to deploy images hosting operating systems
   whose configuration is not supported by snf-image.

 * **EXCLUDE_TASK_<task_name>=yes**
   This family of properties gives the ability to exclude individual
   configuration tasks from running. Hence, if the property
   *EXCLUDE_TASK_DeleteSSHKeys* with a value other than null is passed to
   *snf-image*, the aforementioned configuration step will not be executed, and
   the SSH Keys found in the image will not be removed during the deployment.
   Task exclusion provides great flexibility, but it needs to be used with
   great care. Tasks depend on each other and although those dependencies are
   well documented, automatic task dependency resolution isn't yet supported in
   *snf-image*. If you exclude task A but not task B which depends on A, you
   will probably end up with an unsuccessful deployment because B will fail and
   exit in an abnormal way. You can read more about configuration tasks here.


img_properties OS parameter
+++++++++++++++++++++++++++++++

Image properties are passed to snf_image through the img_properties OS
parameter as a simple json string like the one below:

| {
|     "PROPERTY1": "VALUE1",
|     "PROPERTY2": "VALUE2",
|     "PROPERTY3": "VALUE3",
|     ...
|     ...
|     ...
|     "PROPERTYn": "VALUEn"
| }


A real life example for creating a new ganeti instance and passing image
properties to snf-image would probably look more like this:

``gnt-instance add -O img_properties='{"OSFAMILY":"linux"\,"ROOT_PARTITION":"2"\,"USERS":"root guest"}',img_format=diskdump...``

.. _image-personality:

Personality OS Parameter
^^^^^^^^^^^^^^^^^^^^^^^^

This parameter is an extension of the Server Personality notation proposed by
the OpenStack Compute API v1.1 and defines a list of files to be injected into
the image file system.

Format
++++++

The format of this parameter is a JSON array of objects. Each object in the
array supports the following keys:

 * **path**: The absolute path of the file (string)
 * **contents**: The content of the file encoded as a base64 string (string)
 * **owner**: The user ownership of the file (string)
 * **group**: The group ownership of the file (string)
 * **mode**: The permission mode of the file (number)

The first two (path, contents) are mandatory. The others (owner, group, mode)
are optional and their default value is root, root and 0440 respectively.

Example
+++++++

The JSON string below defines two files (*/tmp/test1*, */tmp/test2*) whose
content is ``test1\n`` and ``test2\n``, they are both owned by *root:root* and
their permissions are ``-rw-r--r--`` [#]_

| [
|     {
|         "path": "/tmp/test1",
|         "contents": "dGVzdDENCg==",
|         "owner": "root",
|         "group": "root",
|         "mode": 0644
|     },
|     {
|         "path": "/tmp/test2",
|         "contents": "dGVzdDINCg==",
|         "owner": "root",
|         "group": "root",
|         "mode": 420
|     }
| ]

.. [#] The first mode is in octal representation and the second in decimal.


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

