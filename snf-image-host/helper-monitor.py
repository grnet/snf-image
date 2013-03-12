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
import optparse
import socket
from scapy.all import sniff

LINESIZE = 512
BUFSIZE = 512
PROGNAME = os.path.basename(sys.argv[0])
STDERR_MAXLINES = 10
MAXLINES = 100
MSG_TYPE = 'image-helper'

PROTOCOL = {
    'TASK_START': ('task-start', 'task'),
    'TASK_END': ('task-end', 'task'),
    'WARNING': ('warning', 'messages'),
    'STDERR': ('error', 'stderr'),
    'ERROR': ('error', 'messages')}


def parse_options(input_args):
    usage = "Usage: %prog [options] <file-sescriptor>"
    parser = optparse.OptionParser(usage=usage)

    parser.add_option("-i", "--interface", type="string", dest="ifname",
                      default=None, metavar="IFNAME",
                      help="listen on interface IFNAME for monitoring data")

    parser.add_option("-f", "--filter", type="string", dest="filter",
        help="add FILTER to incomint traffice when working on an interface",
        default=None, metavar="FILTER")

    options, args = parser.parse_args(input_args)

    if len(args) != 1:
        parser.error('Wrong number of argumets')

    options.fd = args[0]

    if options.filter is not None and options.ifname is None:
        parser.error('You need to define an interface since filters are' \
                     'defined')

    return options


def error(msg):
    sys.stderr.write("HELPER-MONITOR ERROR: %s\n" % msg)
    sys.exit(1)


class HelperMonitor(object):
    def __init__(self, fd):
        self.fd = fd
        self.lines_left = 0
        self.line_count = 0
        self.stderr = ""
        self.line = ""

    def process(self, data):
        if not data:
            if not self.line:
                return
            else:
                data = '\n'

        while True:
            split = data.split('\n', 1)
            self.line += split[0]
            if len(split) == 1:
                if len(self.line) > LINESIZE:
                    error("Line size exceeded the maximum allowed size")
                break

            data = split[1]

            self.line_count += 1
            if self.line_count >= MAXLINES + 1:
                error("Exceeded maximum allowed number of lines: %d." %
                      MAXLINES)

            if self.lines_left > 0:
                self.stderr += "%s\n" % self.line
                self.lines_left -= 1
                if self.lines_left == 0:
                    self.send("STDERR", self.stderr)
                    self.stderr = ""
                self.line = ""
                continue

            self.line = self.line.strip()
            if len(self.line) == 0:
                continue

            if self.line.startswith("STDERR:"):
                m = re.match("STDERR:(\d+):(.*)", self.line)
                if not m:
                    error("Invalid syntax for STDERR line")
                try:
                    self.lines_left = int(m.group(1))
                except ValueError:
                    error("Second field in STDERR line must be an integer")

                if self.lines_left > STDERR_MAXLINES:
                    error("Too many lines in the STDERR output")
                elif self.lines_left < 0:
                    error("Second field of STDERR: %d is invalid" % self.lines_left)

                if self.lines_left > 0:
                    self.stderr = m.group(2) + "\n"
                    self.lines_left -= 1

                if self.lines_left == 0:
                    self.send("STDERR", self.stderr)
                    self.stderr = ""
            elif self.line.startswith("TASK_START:") \
                or self.line.startswith("TASK_END:") \
                or self.line.startswith("WARNING:") \
                or self.line.startswith("ERROR:"):
                (msg_type, _, value) = self.line.partition(':')

                if self.line.startswith("WARNING:") or \
                    self.line.startswith("ERROR:"):
                    value = [value]
                self.send(msg_type, value)
            else:
                error("Unknown command!")

            # Remove the processed line
            self.line = ""

    def send(self, msg_type, value):
        subtype, value_name = PROTOCOL[msg_type]

        msg = {}
        msg['type'] = MSG_TYPE
        msg['subtype'] = subtype
        msg[value_name] = value
        msg['timestamp'] = time.time()
        os.write(self.fd, "%s\n" % json.dumps(msg))


if __name__ == "__main__":
    options = parse_options(sys.argv[1:])

    try:
        fd = int(options.fd)
    except ValueError:
        error("File descriptor is not an integer")

    try:
        os.fstat(fd)
    except OSError:
        error("File descriptor is not valid")

    monitor = HelperMonitor(fd)

    if options.ifname is not None:
        try:
            sniff(filter=options.filter, iface=options.ifname,
                prn=lambda x: monitor.process(x.payload.getfieldval("load")))
        except socket.error as e:
            # Network is down
            if e.errno == 100:
                monitor.process(None)
            else:
                raise
    else:
        while True:
            data = os.read(sys.stdin.fileno(), BUFSIZE)
            monitor.process(data)
            if not data:
                break

# vim: set sta sts=4 shiftwidth=4 sw=4 et ai :
