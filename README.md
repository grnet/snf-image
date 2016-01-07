snf-image
=========

Overview
--------

This is snf-image, a [Ganeti](http://code.google.com/p/ganeti) OS provider
primarily used by the Synnefo cloud management software to deploy VM instances
from predefined or custom Images.

It comprises two distinct components:
* snf-image-host, which executes as a privileged process on the Ganeti host
* snf-image-helper, which executes inside a helper VM and undertakes all
  security-sensitive customization of a Ganeti VM.

Project Page
------------

Please see the [official Synnefo site](http://www.synnefo.org) and the
[latest snf-image docs](http://www.synnefo.org/docs/snf-image/latest/index.html)
for more information.


Copyright and license
=====================

Copyright (C) 2011-2016 GRNET S.A. and individual contributors.

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
02110-1301, USA.
