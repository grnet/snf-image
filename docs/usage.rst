Usage
=====

Ganeti OS Interface
^^^^^^^^^^^^^^^^^^^

*snf-image* requires ganeti-os-interface v20 to operate and it introduces the
following OS Parameters:

 * **img_format** (required if *config_url* is missing): the image format type
   (:ref:`details <image-format>`)
 * **img_id** (required if *config_url* is missing): the URI used to identify the
   image (:ref:`details <image-id>`)
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

Right now 3 different types of image formats are supported:

 * **extdump**: a raw dump of an ext{2,3,4} file system
 * **ntfsdump**: a raw dump of an NTFS file system
 * **diskdump**: a raw dump of a disk

extdump and ntfsdump image formats
++++++++++++++++++++++++++++++++++

Those two formats are dumps (raw copies using dd) of partitions hosting Linux
systems on ext{2,3,4} and Windows systems on ntfs filesystems respectively.
Partitions hosting a Windows or Linux system that are suitable for dumping
should have the following properties:

 * Be the first partition in the filesystem
 * The OS they host should not depend on any other partitions
 * Start at sector 2048
 * Have a bootloader installed in the boot sector of the partition (not MBR)
 * Have the root device in */etc/fstab* specified in a persistent way, using
   UUID or LABEL (for extdump only)

Known Issues
------------

 * For linux systems, having grub installed in the partition is fragile and
   things can go wrong when resizing the partitions, especially when shrinking.
 * More complicated partition schemes are not supported.

diskdump image format
+++++++++++++++++++++

Diskdump is a newer format that overcomes most of the aforementioned issues.
This format is a dump (raw copy using dd) of a whole disk.

This design decision has the following benefits:

 * Swap partitions are supported
 * The system may use multiple partitions:
    * dedicated partitions for /boot, /home etc in linux
    * system and boot partition in Windows
 * There are no restrictions on starting sectors of partitions

Although diskdump is a lot more flexible than the older formats, there are
still some rules to follow:

 * All devices in fstab should be specified by persistent names (UUID or LABEL)
 * LVMs are not supported
 * For Linux disks only ext{2,3,4} file systems are supported
 * For FreeBSD disks only UFS file systems are supported
 * For FreeBSD only GUID Partition Tables (GPT) are supported

.. _image-id:

Image IDs & Storage back-ends
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

*snf-image* can use images that are stored in a variety of different back-ends.
The back-end to be used is determined by the value passed by the *img_id* OS
parameter. The following backends are supported:

 * **Local back-end**:
   The local back-end is used to retrieve images that are stored in the ganeti
   node that the image deployment takes place. The local back-end is used if the
   value of the *img_id* ganeti OS parameter is either prefixed with *file://* or
   is not prefixed at all. All local images are expected to be found under a
   predifined image directory. By default */var/lib/snf-image* is used, but the
   user can change thi directory by overwriting the value of the *IMAGE_DIR*
   variable under */etc/default/snf-image*. The name of the image file is created
   by adding the image type extension in the end of the *img_id*. If the *img_id*
   for example is *file://slackware* and the image type is *diskdump*, snf-image
   will expect to find an image file under the following path:
   ``/usr/lib/snf-image/slackware.diskdump``

 * **Network back-end**:
   The network back-end is used to retrieve images that are accessible from the
   network. If the *imd_id* starts with *http:*, *https:*, *ftp:* or *ftps:*,
   snf-image will treat the *img_id* as a remote URL and will try to fetch the
   image using `cURL <http://curl.haxx.se/>`_.

 * **Pithos back-end**:
   If an *img_id* is prefixed with *pithos:* or *pithosmap:*, the image is
   considered to be pithos back-ended. *snf-image* contains a special command-line
   tool (*pithcat*) for retrieving this kind of images. For *pithosmap:* images,
   the user needs to have set a valid value for the PITHOS_DATA variable.
   For *pithos:* images, in addition to PITHOS_DATA, the PITHOS_DB variable needs
   to contain a valid value. */etc/default/snf-image* may be used to set both
   values.

 * **Null back-end**:
   The null back-end is used if the *img_id* value is *null*. In this case no
   image copying is performed. This is handy if the hard disk already contains the
   image data before *snf-image* is executed (for example if the hard disk is a
   snapshot of an existing VM's hard disk).

.. _image-properties:

Image Properties
^^^^^^^^^^^^^^^^

In order for snf-image to be able to properly configure an image, it may make
use of a set of image properties. Those image properties are passed to
snf-image by Ganeti through the img_poroperties OS parameter (see Ganeti OS
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

Image properties are passed to snf_image through the img_properties OS parameter as a simple json string like the one below:

| {
|     "PROPERTY1": "VALUE1",
|     "PROPERTY2": "VALUE2",
|     "PROPERTY3": "VALUE3",
|     ...
|     ...
|     ...
|     "PROPERTYn": "VALUEn"
| }


A real life example for creating a new ganeti instance and passing image properties to snf-image would probably look more like this:

``gnt-instance add -O img_properties='{"OSFAMILY":"linux"\,"ROOT_PARTITION":"2"\,"USERS":"root guest"}',img_format=diskdump...``

.. _image-personality:

Personality OS Parameter
^^^^^^^^^^^^^^^^^^^^^^^^

This parameter is an extension of the Server Personality notation proposed by
the OpenStack Compute API v1.1 and defines a list of files to be injected into
the image filesystem.

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
