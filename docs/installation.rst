Installation
============

Before installing snf-image be sure to have a working Ganeti installation in
your cluster. The installation process should take place in **all** Ganeti
nodes. Here we will describe the installation in a single node. The process is
identical for all nodes and should be repeated manually or automatically, e.g.,
with puppet.

Installing snf-image using packages
-----------------------------------

Debian GNU/Linux
^^^^^^^^^^^^^^^^

For Debian 7.x (Wheezy) we provide packages in our APT repository. To use
our repository add the following lines to file ``/etc/apt/sources.list``:

``deb http://apt.dev.grnet.gr wheezy/``

``deb-src http://apt.dev.grnet.gr wheezy/``

After you update ``/etc/apt/sources.list`` import the repo's GPG key:

.. code-block:: console

  # curl https://dev.grnet.gr/files/apt-grnetdev.pub | apt-key add -

To install the package use the following commands:

.. code-block:: console

  # apt-get update
  # apt-get install snf-image

The last command will also download and install the *snf-image-helper* image in
the post install phase of the package installation.

Ubuntu
^^^^^^

For Ubuntu 14.04 LTS we provide packages in our APT repository. To use our
repository add the following lines to file ``/etc/apt/sources.list``:

``deb http://apt.dev.grnet.gr trusty/``

``deb-src http://apt.dev.grnet.gr trusty/``

After you update ``/etc/apt/sources.list`` import the repo's GPG key:

.. code-block:: console

  # curl https://dev.grnet.gr/files/apt-grnetdev.pub | apt-key add -

To install the package use the following commands:

.. code-block:: console

  # apt-get update
  # apt-get install snf-image

The last command will also download and install the *snf-image-helper* image in
the post install phase of the package installation.

CentOS
^^^^^^

For CentOS 6.5 we provide packages in our Yum repository.

To add the GRNET repository in your system, run:

.. code-block:: console

  # yum localinstall https://dev.grnet.gr/files/grnet-repo.rpm

You can verify the authenticity of the package using our public key found
`here <https://dev.grnet.gr/files/apt-grnetdev.pub>`_.

To install snf-image run:

.. code-block:: console

  # yum install snf-image

The last command will also download and install the *snf-image-helper* image in
the post install phase of the package installation.

Installing snf-image from source
--------------------------------

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

  # make install
  # install -Dm600 defaults /etc/default/snf-image
  # mkdir -p /var/lib/snf-image/helper

Finally, install the helper image by executing:

.. code-block:: console

  # snf-image-update-helper

