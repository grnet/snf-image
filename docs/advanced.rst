Advanced Topics
===============

.. _image-format-advanced:

Image Format
^^^^^^^^^^^^

snf-image supports 3 types of image formats:

 * **extdump**: a raw dump of an ext{2,3,4} file system
 * **ntfsdump**: a raw dump of an NTFS file system
 * **diskdump** (recommended): a raw dump of a disk

extdump and ntfsdump image formats
++++++++++++++++++++++++++++++++++

Those two formats are dumps (raw copies using dd) of partitions hosting Linux
systems on ext{2,3,4} and Windows systems on NTFS file systems respectively.
Partitions hosting a Windows or Linux system that are suitable for dumping
should have the following properties:

 * Be the first partition in the file system
 * The OS they host should not depend on any other partitions
 * Start at sector 2048
 * Have a boot loader installed in the boot sector of the partition (not MBR)
 * Have the root device in */etc/fstab* specified in a persistent way, using
   UUID or LABEL (for extdump only)

Known Issues
------------

 * For Linux systems, having GRUB installed on a partition is fragile and
   things can go wrong if you shrink the partition.
 * More complicated partition schemes are not supported.

diskdump image format (recommended)
+++++++++++++++++++++++++++++++++++

Diskdump is a newer format that overcomes most of the aforementioned issues.
This format is a dump (raw copy using dd) of a whole disk.

This design decision has the following benefits:

 * Swap partitions are supported
 * The system may use multiple partitions:
    * Dedicated partitions for /boot, /home etc. in Linux
    * Separate system and boot partition in Windows
 * There are no restrictions on starting sectors of partitions

Although diskdump is a lot more flexible than the older formats, there are
still some rules to follow:

 * For Linux:
   * All block devices in */etc/fstab* should be specified using persistent
     names (UUID or LABEL)
   * LVM partitions are not supported
   * Only ext{2,3,4} file systems are supported
 * For FreeBSD:
   * GUID Partition Tables (GPT) should be used
   * Only UFS2 file systems are supported
   * Labels should be omitted in */etc/fstab* entries
 * For {Open,Net}BSD:
   * Only FFS file systems should be used

Progress Monitoring Interface
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

*snf-image* has an embedded mechanism for transmitting progress messages during
an image deployment. A user may specify an external executable by overwriting
the *PROGRESS_MONITOR* variable under ``/etc/default/snf-image`` and
*snf-image* will redirect the progress messages to the standard input of this
program. In this section we will describe the format and the fields of the
progress messages.

The progress messages are JSON strings with standardized fields. All messages
have a **type** field whose value is a string and a **timestamp** field whose
value is a floating point number referring to a time encoded as the number of
seconds elapsed since the epoch. The rest of the field depend on the specific
type.

image-info
++++++++++

This message type is used to display arbitrary progress information. It has an
extra *messages* field whose value is a list of strings. A valid ``image-info``
message looks like this:

``{"messages": ["Starting image copy..."], "type": "image-info", "timestamp": 1378914866.209169}``

image-error
+++++++++++

This message type is used to display a fatal error that occurred during image
deployment. It may either have an extra *messages* field to display the error
message or an *stderr* field to display the last lines of the standard error
output stream of the OS creation script. Valid ``image-error`` messages look
like this:

``{"messages": ["Image customization failed."], "type": "image-error", "timestamp": 1379507045.924449}``

image-copy-progress
+++++++++++++++++++

One of the tasks *snf-image* has to accomplish is to copy the image file into
the VM's hard disk before configuring it. Messages of type
``image-copy-progress`` are used to display the progress of this task. The extra
fields this message type has is *position*, *total* and *progress*. The
*position* field is used to display the number of bytes written to the hard
disk. The *total* field indicates the overall size (in bytes) of the image, and
finally the *progress* field indicates the percent of the accomplished work.
Messages of this type look like this:

``{"position": 335547996, "total": 474398720, "type": "image-copy-progress", "timestamp": 1378914869.312985, "progress": 70.73}``

image-helper
++++++++++++

This is a family of messages that are created when *snf-image-helper* runs.
Each message of this type has a *subtype* field.

task-start
----------

Messages with *subtype* ``task-start`` indicate that *snf-image-helper*
started running a :ref:`configuration task <image-configuration-tasks>` on the
image. Messages of this type have an extra *task* field whose value is the
name of the task *snf-image-helper* started, and look like this:

``{"subtype": "task-start", "task": "FixPartitionTable", "type": "image-helper", "timestamp": 1379507040.456931}``

task-stop
---------

Messages with *subtype* ``task-stop`` are produced every time a configuration
task successfully exits. As with the ``task-start`` messages, the *task* field
is present:

``{"subtype": "task-end", "task": "FixPartitionTable", "type": "image-helper", "timestamp": 1379507041.357184}``

warning
-------

This messages are produced to display a warning. The actual warning message
itself is present in the *messages* field:

``{"subtype": "warning", "type": "image-helper", "messages": ["No swap partition defined"], "timestamp": 1379075807.71704}``

error
-----

The last ``image-helper`` message that may occur is the ``error`` message. As
with the ``image-error`` messages, either a *messages* field that hosts the
actual error message or a *stderr* field that hosts the last 10 lines of the
standard error output stream of *snf-image-helper*. Valid *error* messages look
like this:

``{"subtype": "error", "type": "image-helper", "messages": ["The image contains a(n) MSDOS partition table.  For FreeBSD images only GUID Partition Tables are supported."], "timestamp": 1379507910.799365}``
