#!/usr/bin/env python

# Copyright (C) 2012 GRNET S.A.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.

"""Decode a json encoded string with properties

This program decodes a json encoded properties string and outputs it in a
bash sourcable way. The properties are passed to the program through a JSON
string either read from a file or from standard input and are outputed to a
target file.
"""

import sys
import os
import subprocess
import json
import random
import string
from StringIO import StringIO


def main():
    options = sys.argv[1:]

    prefix = ''.join(random.choice(string.ascii_uppercase) for x in range(8))

    config = json.load(sys.stdin)

    for key, value in config.items():
        if str(key).upper() in options:
            os.environ[prefix + str(key).upper()] = value

    p = subprocess.Popen(['bash', '-c', 'set'], stdout=subprocess.PIPE)
    output = StringIO(p.communicate()[0])
    for line in iter(output):
        if line.startswith(prefix):
            print line[len(prefix):]

    return 0


if __name__ == "__main__":
    sys.exit(main())

# vim: set sta sts=4 shiftwidth=4 sw=4 et ai :
