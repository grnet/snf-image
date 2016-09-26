Development
===========

Building a new snf-image-helper kernel
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The kernel used to boot the helper VM is custom. We build our own kernel
because the ones shipped with the major Linux distributions don't have UFS
write support enabled, since it is considered dangerous. The ability to write
to UFS file systems is needed in order to support the various \*BSD images. In
this tutorial we will show how to build a Debian Kernel package using the
kernel configuration shipped with the snf-image. The kernel configuration file
we provide with snf-image is stripped down. All unnecessary hardware drivers
are removed and only the ones that are needed to boot a KVM and a XEN guest are
left. In order to recompile a Debian kernel using our configuration file do the
following:

Install the dependencies
++++++++++++++++++++++++

Install the dependencies for compiling a kernel:

.. code-block:: console

 # apt-get install build-essential fakeroot
 # apt-get build-dep linux

Download the kernel package:

.. code-block:: console

 $ apt-get source linux


Build the packages
++++++++++++++++++

Apply the existing patches:

.. code-block:: console

 $ fakeroot debian/rules source

Setup the amd64 configuration:

.. code-block:: console

 $ cd linux-<version>
 $ fakeroot make -f debian/rules.gen setup_amd64_none

Copy the snf-image provided configuration to the new kernel:

.. code-block:: console

 $ cp /usr/share/doc/snf-image/kconfig-* debian/build/build_amd64_none_amd64/.config

Apply the kernel configuration:

.. code-block:: console

 $ make -C debian/build/build_amd64_none_amd64 oldconfig
 $ cp debian/build/build_amd64_none_amd64/.config debian/build/config.amd64_none_amd64

Change the ABI name (the debian building system will complain otherwise):

.. code-block:: console

 $ sed -i 's|abiname: .\+|abiname: 0.snf.image.helper.1|' debian/config/defines

Add a new entry in ``debian/changelog`` with ``jessie-helper`` as distribution:

.. code-block:: console

 $ dch -D jessie-helper --force-distribution

Build the new kernel package:

.. code-block:: console

 $ fakeroot make -j <num> -f debian/rules.gen binary-arch_amd64_none

Upload it to an apt repository
++++++++++++++++++++++++++++++

If you want to upload the package to a repository, you will need to create a
changes file:

.. code-block:: console

 $ cp ../linux_<old_version>.dsc ../linux-<new_version>.dsc
 $ dpkg-genchanges > ../lunux_<new_version>.changes

And sign it:

.. code-block:: console

 $ debsign ../linux_<new_version>.changes

Now you can use ``dput`` or ``dupload`` to upload the package to a repository.

