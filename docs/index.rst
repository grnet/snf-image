.. snf-image documentation master file, created by
   sphinx-quickstart on Fri Sep 13 16:50:13 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to snf-image's documentation!
=====================================

.. image:: images/logo.png

snf-image is a `Ganeti <http://code.google.com/p/ganeti/>`_ OS definition. It
allows Ganeti to launch instances from predefined or untrusted custom Images.
The whole process of deploying an Image onto the block device, as provided by
Ganeti, is done in complete isolation from the physical host, enhancing
robustness and security.

snf-image supports `KVM <http://www.linux-kvm.org/page/Main_Page>`_ and
`Xen <http://www.xenproject.org/>`_ based Ganeti clusters.

snf-image also supports Image customization via hooks. Hooks allow for:

 * Changing the password of root or arbitrary users
 * Injecting files into the file system, e.g., SSH keys
 * setting a custom hostname
 * re-creating SSH host keys to ensure the image uses unique keys

snf-image is being used in large scale production environments with Ganeti to
successfully deploy many major Linux distributions (Debian, Ubuntu/Kubuntu,
CentOS, Fedora, OpenSUSE, Slackware, Arch Linux, CoreOS), Windows Server
flavors (2008 R2, 2012, 2012 R2), as well as BSD systems (FreeBSD, OpenBSD,
NetBSD). It is also known to work well with current Desktop versions of Windows
(7, 8, 8.1) as well as Windows XP.

The snf-image Ganeti OS Definition is released under
`GPLv2 <http://www.gnu.org/licenses/gpl-2.0.html>`_.


Contents:
^^^^^^^^^

.. toctree::
   :maxdepth: 2

   architecture
   interface
   installation
   configuration
   usage
   advanced
   development
   design

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
