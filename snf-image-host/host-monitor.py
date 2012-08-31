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

"""Utility that generates monitoring messages for snf-image.

This utility given a message type as option and the message body as input will
print a monitoring message to stdout.
"""

import sys
import os
import json
import time

MSG_TYPE_ERROR = "image-error"
MSG_TYPE_INFO = "image-info"

PROTOCOL = {
    "error": (MSG_TYPE_ERROR, "messages"),
    "stderr": (MSG_TYPE_ERROR, "stderr"),
    "info": (MSG_TYPE_INFO, "messages")
}

PROGNAME = os.path.basename(sys.argv[0])

if __name__ == "__main__":
    usage = "Usage: %s <msg-type>\n" % PROGNAME

    if len(sys.argv) != 2:
        sys.stderr.write(usage)
        sys.exit(1)

    msg_type = sys.argv[1]

    if msg_type  not in PROTOCOL.keys():
        sys.stderr.write("Unknown message type: %s\n" % msg_type)
        sys.exit(1)

    msg = {}
    msg['type'] = PROTOCOL[msg_type][0]

    lines = []
    if msg_type == 'stderr':
        msg['stderr'] = sys.stdin.read()
    else:
        while True:
            line = sys.stdin.readline()

            if not line:
                break

            lines.append(line.strip())
        msg[PROTOCOL[msg_type][1]] = lines

    msg['timestamp'] = time.time()
    sys.stdout.write("%s\n" % json.dumps(msg))

    sys.exit(0)

# vim: set sta sts=4 shiftwidth=4 sw=4 et ai :
