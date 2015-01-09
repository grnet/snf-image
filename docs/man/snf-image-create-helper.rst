:orphan:

snf-image-create-helper manual page
===================================

Synopsis
--------

**snf-image-create-helper** [OPTIONS]

Description
-----------
Run multistrap and create a small Debian image populated with the
snf-image-helper package. This image is needed by ganeti's \`snf-image' guest
OS type to work.

Options
-------

-d DIRECTORY
    Use this directory to host the created files instead of the default
    [default: $HELPER_DIR]

-h  Print this message

-p PACKAGE
    Install this deb package in the helper image, instead of the default

-y  Assume Yes to all queries and do not prompt

Files
-----

/etc/default/snf-image
    Configuration file

/etc/snf-image/multistrap.conf
    Multistrap configuration file

/etc/snf-image/apt.pref.d
    Directory hosting APT preference files to be used during multistrap

