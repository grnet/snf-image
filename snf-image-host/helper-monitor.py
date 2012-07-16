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
import time
import json
import re

LINESIZE = 512
PROGNAME = os.path.basename(sys.argv[0])
STDERR_MAXLINES = 10
MAXLINES = 100

PROTOCOL = {
    'TASK_START': ('task-start', 'task'),
    'TASK_END': ('task-end', 'task'),
    'WARNING': ('warning', 'msg'),
    'STDERR': ('error', 'stderr'),
    'ERROR': ('error', 'msg')}


def error(msg):
    sys.stderr.write("helper-monitor error: %s\n" % msg)
    sys.exit(1)


def send(fd, msg_type, value):
    subtype, value_name = PROTOCOL[msg_type]

    msg = {}
    msg['type'] = 'helper'
    msg['subtype'] = subtype
    msg[value_name] = value
    msg['timestamp'] = time.time()
    os.write(fd, "%s\n" % json.dumps(msg))


if __name__ == "__main__":
    usage = "Usage: %s <file-descriptor>\n" % PROGNAME

    if len(sys.argv) != 2:
        sys.stderr.write(usage)
        sys.exit(1)

    try:
        fd = int(sys.argv[1])
    except ValueError:
        error("File descriptor is not an integer")

    try:
        os.fstat(fd)
    except OSError:
        error("File descriptor is not valid")

    lines_left = 0
    stderr = ""

    line_count = 0
    while 1:
        line = sys.stdin.readline(LINESIZE)

        if not line:
            break
        else:
            line_count += 1

        if line[-1] != '\n':
            # Line is too long...
            error("Too long line...")
            sys.exit(1)

        if lines_left > 0:
            stderr += line
            lines_left -= 1
            if lines_left == 0:
                send(fd, "STDERR", stderr)
                stderr = ""
            continue

	if line_count >= MAXLINES + 1:
            error("Maximum allowed helper monitor number of lines exceeded.")

        line = line.strip()
        if len(line) == 0:
            continue

        if line.startswith("STDERR:"):
            m = re.match("STDERR:(\d+):(.*)", line)
            if not m:
                error("Invalid syntax for STDERR line")
            try:
                lines_left = int(m.group(1))
            except ValueError:
                error("Second field in STDERR line must be an integer")

            if lines_left > STDERR_MAXLINES:
                error("Too many lines in the STDERR output")
            elif lines_left < 0:
                error("Second field of STDERR: %d is invalid" % lines_left)

            if lines_left > 0:
                stderr = m.group(2) + "\n"
                lines_left -= 1

            if lines_left == 0:
                send(fd, "STDERR", stderr)
                stderr = ""
        elif line.startswith("TASK_START:") or line.startswith("TASK_END:") \
            or line.startswith("WARNING:") or line.startswith("ERROR:"):
            (msg_type, _, value) = line.partition(':')
            send(fd, msg_type, value)
        else:
            error("Unknown command!")

# vim: set sta sts=4 shiftwidth=4 sw=4 et ai :
