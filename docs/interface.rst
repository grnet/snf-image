Interface
=========

Ganeti OS Interface
^^^^^^^^^^^^^^^^^^^

*snf-image* requires ganeti-os-interface v20 to operate and it introduces the
following OS Parameters:

 * **img_format** (required if *config_url* is missing): the image format type
   (:ref:`details <image-format>`)
 * **img_id** (required if *config_url* is missing): the URI used to identify
   the image (:ref:`details <image-id>`)
 * **img_passwd** (optional): the password to be injected into the image
   (:ref:`details <image-passwd>`)
 * **img_properties** (optional): additional image properties used to customize
   the image (:ref:`details <image-properties>`)
 * **img_personality** (optional): files to be injected into the image's file
   system (:ref:`details <image-personality>`)
 * **config_url** (optional): the URL to download configuration data from

.. _image-format:

Image Format (img_format)
^^^^^^^^^^^^^^^^^^^^^^^^^

snf-image supports 3 different types of image formats:

 * **diskdump** (recommended): a raw dump of a disk
 * **extdump**: a raw dump of an ext{2,3,4} file system
 * **ntfsdump**: a raw dump of an NTFS file system

These are also the only valid values for the **img_format** OS parameter.
The **diskdump** type is the newest and recommended type. Thus, all sample
images we provide are of this type. For more details about the internals of
image formats please see the corresponding :ref:`advanced section
<image-format-advanced>`.

.. _image-id:

Image ID (img_id)
^^^^^^^^^^^^^^^^^

The **img_id** OS parameter points to the actual Image that we want to deploy.
It is a URI and its prefix denotes the type of :ref:`backend <storage-backends>`
to be used. If no prefix is used, it defaults to the local back-end:

 * **Local backend**:
   To select it, the prefix should be ``local://``, followed by the name of the
   image. All local images are expected to be found under a predefined image
   directory (``/var/lib/snf-image`` by default).

  | For example, if we want to deploy the image file:
  | ``/var/lib/snf-image/slackware.diskdump``
  | We need to assign:
  | ``img_id=local://slackware.diskdump``

 * **Network backend**:
   If the **imd_id** starts with ``http:``, ``https:``, ``ftp:`` or ``ftps:``,
   snf-image will treat the **img_id** as a remote URL and will try to fetch the
   image using `cURL <http://curl.haxx.se/>`_.

  | For example, if we want to deploy an image from an http location:
  | ``img_id=http://www.synnefo.org/path/to/image/slackware-image``

 * **Pithos backend**:
   If the **img_id** is prefixed with ``pithos://`` or ``pithosmap://`` the
   image is considered to reside on a Pithos deployment. For ``pithosmap://``
   images, the user needs to have set a valid value for the ``PITHOS_DATA``
   variable in snf-image's configuration file (``/etc/default/snf-image`` by
   default) if the storage backend is ``nfs`` or ``PITHOS_RADOS_POOL_MAPS`` and
   ``PITHOS_RADOS_POOL_BLOCKS`` if the storage backend is ``rados``.
   For ``pithos://`` images, in addition to ``PITHOS_DATA`` or
   ``PITHOS_RADOS_POOL_*``, the user needs to have set a valid value for the
   ``PITHOS_DB`` variable, too.

  | For example, if we want to deploy using a full Pithos URI:
  | ``img_id=pithos://<user-uuid>/<container>/<slackware-image>``
  | or if we already know the map:
  | ``img_id=pithosmap://<slackware-image-map-name>/<size>``

 * **Null backend**:
   To select the Null back-end and skip the fetching and extraction step, we set
   ``img_id=null``.

.. _image-passwd:

Image Password (img_passwd)
^^^^^^^^^^^^^^^^^^^^^^^^^^^

The value of this parameter is the password to be injected into the image. If
this parameter is not set at all, then the *ChangePassword* task (see
:ref:`Image Configuration Tasks <image-configuration-tasks>`) will not run.

.. _image-properties:

Image Properties (img_properties)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

*snf-image* may use a number of properties to properly configure the image.
Those image properties are passed to snf-image by Ganeti through the
*img_poroperties* OS parameter (see Ganeti OS Interface). The name of all image
properties is case-insensitive. For the diskdump format some properties are
mandatory. For {ext,ntfs}dump formats all image properties are optional.

We can group image properties in two categories:

1. Generic properties (*OSFAMILY*, *ROOT_PARTITION*, *USERS*)
2. Configuration tasks to run (*EXCLUDE_ALL_TASKS*, *EXCLUDE_TASK_<task_name>*)
   (see here for :ref:`valid configuration tasks <image-configuration-tasks>`)

A list of all properties follows:

Mandatory properties (for diskdump only)
++++++++++++++++++++++++++++++++++++++++

 * **OSFAMILY=linux|windows|freebsd|netbsd|openbsd**
   This specifies whether the image is a Linux, a Windows or a \*BSD Image.
   {ext,ntfs}dump formats are self descriptive regarding this property.
 * **ROOT_PARTITION=n**
   This specifies the partition number of the root partition. As mentioned
   earlier, for now, only primary partitions are supported. This property is
   trivial for {ext,ntfs}dump formats (they only host one partition).

Optional properties
+++++++++++++++++++

 * **USERS="username1 username2...."**
   This is a space-separated list of users, whose password will be reset by
   *snf-image*. The use of this property is optional, but highly recommended.
   For now, if this property is missing, the users are chosen according to a
   set of rules, but those rules may change or even be dropped in the future.
   The rules we currently use are listed below:

     * For Windows images, the *Administrator*'s password is reset.
     * For Linux and \*BSD images, the *root* password is reset.

 * **DO_SYNC=yes**
   By default in ResizeUnmounted task, when ``resize2fs`` is executed to
   enlarge a ext[234] file system, ``fsync()`` is disabled to speed up the
   whole process. If for some reason you need to disable this behavior, use the
   *DO_SYNC* image property.

 * **PASSWORD_HASHING_METHOD=md5|sha1|blowfish|sha256|sha512**
   This property can be used on Unix instances to specify the method to be used
   to hash the users password. By default this is determined by the type of the
   instance. For Linux and FreeBSD instances ``sha512`` is used, for OpenBSD
   ``blowfish`` and for NetBSD ``sha1``. Use this property with care. Most
   systems don't support all hashing methods (see
   `here <http://pythonhosted.org/passlib/modular_crypt_format.html#mcf-identifiers>`_
   for more info).

 * **SWAP=<partition id>:<size>**
   If this property is defined, *snf-image* will create a swap partition with
   the specified size in MB. The *partition id* is the number that the Linux
   kernel will assign to this partition. For example, if you have a disk with
   an MSDOS  partition table on it and one primary partition, the image
   property *SWAP=2:512* would instruct *snf-image* to create a 512MB long
   primary partition for swap with id=2. On the other hand, if the SWAP
   property had this form: *SWAP=5:512*, since primary partitions may have an
   id from 1 to 4, *snf-image* would create a 512MB extended partition with
   id=2 and a logical swap partition with id=5 in it with the same size. This
   property only applies to Linux instances.

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
+++++++++++++++++++++++++++

Image properties are passed to snf_image through the img_properties OS
parameter as a simple JSON string like the one below:

| {
|     "PROPERTY1": "VALUE1",
|     "PROPERTY2": "VALUE2",
|     "PROPERTY3": "VALUE3",
|     ...
|     ...
|     ...
|     "PROPERTYn": "VALUEn"
| }


A real life example for creating a new Ganeti instance and passing image
properties to snf-image looks like this:

.. code-block:: console

   ``gnt-instance add -O img_properties='{"OSFAMILY":"linux"\,"ROOT_PARTITION":"2"\,"USERS":"root guest"}',img_format=diskdump,img_id=...``

.. _image-personality:

Image Personality (img_personality)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This parameter is an extension of the Server Personality notation proposed by
the OpenStack Compute API v1.1 and defines a list of files to be injected into
the image file system.

Format
++++++

The format of this parameter is a JSON array of objects. Each object in the
array supports the following keys:

 * **path**: The absolute path of the file (string)
 * **contents**: The content of the file encoded as a Base64 string (string)
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
