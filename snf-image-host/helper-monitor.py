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

# add HELPER_MONITOR_
LINESIZE = 512+16
BUFSIZE = 512+16
PROGNAME = os.path.basename(sys.argv[0])
STDERR_MAXLINES = 10
MAXLINES = 100
MSG_TYPE = 'image-helper'

PROTOCOL = {
    'HELPER_MONITOR_TASK_START': ('task-start', 'task'),
    'HELPER_MONITOR_TASK_END': ('task-end', 'task'),
    'HELPER_MONITOR_WARNING': ('warning', 'messages'),
    'HELPER_MONITOR_STDERR': ('error', 'stderr'),
    'HELPER_MONITOR_ERROR': ('error', 'messages')}


def error(msg):
    sys.stderr.write("HELPER-MONITOR ERROR: %s\n" % msg)
    sys.exit(1)


def send(fd, msg_type, value):
    subtype, value_name = PROTOCOL[msg_type]

    msg = {}
    msg['type'] = MSG_TYPE
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
    line_count = 0
    stderr = ""
    line = ""
    while True:
        # Can't use sys.stdin.readline since I want unbuffered I/O
        new_data = os.read(sys.stdin.fileno(), BUFSIZE)

        if not new_data:
            if not line:
                break
            else:
                new_data = '\n'

        while True:
            split = new_data.split('\n', 1)
            line += split[0]
            if len(split) == 1:
                if len(line) > LINESIZE:
                    error("Line size exceeded the maximum allowed size")
                break

            new_data = split[1]

            line_count += 1
            if line_count >= MAXLINES + 1:
                error("Exceeded maximum allowed number of lines: %d." %
                      MAXLINES)

            if lines_left > 0:
                stderr += "%s\n" % line
                lines_left -= 1
                if lines_left == 0:
                    send(fd, "HELPER_MONITROR_STDERR", stderr)
                    stderr = ""
                line = ""
                continue

            line = line.strip()
            if len(line) == 0:
                continue

            if line.startswith("HELPER_MONITOR_STDERR:"):
                m = re.match("HELPER_MONITOR_STDERR:(\d+):(.*)", line)
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
                    send(fd, "HELPER_MONITOR_STDERR", stderr)
                    stderr = ""
            elif line.startswith("HELPER_MONITOR_TASK_START:") \
                or line.startswith("HELPER_MONITOR_TASK_END:") \
                or line.startswith("HELPER_MONITOR_WARNING:") \
                or line.startswith("HELPER_MONITOR_ERROR:"):
                (msg_type, _, value) = line.partition(':')

                if line.startswith("HELPER_MONITOR_WARNING:") \
                  or line.startswith("HELPER_MONITOR_ERROR:"):
                    value = [value]
                send(fd, msg_type, value)
            else:
                error("Unknown command!")

            # Remove the processed line
            line = ""

# vim: set sta sts=4 shiftwidth=4 sw=4 et ai :
