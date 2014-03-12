Installation
============

Before installing snf-image be sure to have a working Ganeti installation in
your cluster. The installation process should take place in **all** Ganeti
nodes. Here we will describe the installation in a single node. The process is
identical for all nodes and should be repeated manually or automatically, e.g.,
with puppet.

Installing snf-image using packages
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For Debian GNU/Linux and Ubuntu we provide packages in our APT repository.

For Debian Wheezy add the following lines to ``/etc/apt/sources.list`` file:

``deb http://apt.dev.grnet.gr wheezy/``

``deb-src http://apt.dev.grnet.gr wheezy/``

For Ubuntu 12.04 LTS add the following lines:

``deb http://apt.dev.grnet.gr precise/``

``deb-src http://apt.dev.grnet.gr precise/``

After you update ``/etc/apt/sources.list`` import the repo's GPG key:

.. code-block:: console

  $ curl https://dev.grnet.gr/files/apt-grnetdev.pub | apt-key add -

To install the package use the following commands:

.. code-block:: console

  $ apt-get update
  $ apt-get install snf-image

The last command will also download and install the *snf-image-helper* image in
the post install phase of the package installation.

Installing snf-image from source
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To install snf-image from source, download the provided source package:

.. code-block:: console

  $ wget http://apt.dev.grnet.gr/wheezy/snf-image_<VERSION>.orig.tar.gz

Untar, configure and build the source:

.. code-block:: console

  $ tar -xvf snf-image_<VERSION>.orig.tar.gz
  $ cd snf-image_<VERSION>/snf-image-host
  $ ./autogen.sh
  $ ./configure --prefix=/usr --sysconfdir=/etc --localstatedir=/var
  $ make

Install snf-image:

.. code-block:: console

  $ make install
  $ install -Dm600 defaults /etc/default/snf-image
  $ mkdir -p /var/lib/snf-image/helper

Finally, install the helper image by executing:

.. code-block:: console

  $ snf-image-update-helper

