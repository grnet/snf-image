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

import sys
import os
import json
import time

PROGNAME = os.path.basename(sys.argv[0])

if __name__ == "__main__":
    usage="Usage: %s <msg-type>\n" % PROGNAME
    
    if len(sys.argv) != 2:
        sys.stderr.write(usage)
        sys.exit(1)

    msg = {}
    msg['type'] =  sys.argv[1]
    msg['stderr'] = sys.stdin.read()
    msg['timestamp'] = time.time()

    sys.stdout.write("%s\n" % json.dumps(msg))

    sys.exit(0)

# vim: set sta sts=4 shiftwidth=4 sw=4 et ai :
