#!/usr/bin/env python
#
# Copyright (C) 2011 GRNET S.A.
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

"""Inject files into a directory

This program injects files into a target directory.
The files are passed to the program through a JSON string either read from a
file or from standard input.

"""

import sys
import os
import json
import datetime
import base64
from optparse import OptionParser


def timestamp():
    now = datetime.datetime.now()
    current_time = now.strftime("%Y%m%d.%H%M%S")
    return current_time


def parse_arguments(input_args):
    usage = "Usage: %prog [options] <target>"
    parser = OptionParser(usage=usage)
    parser.add_option("-i", "--input",
                      action="store", type='string', dest="input_file",
                      help="get input from FILE instead of stdin",
                      metavar="FILE")
    parser.add_option("-d", "--decode", action="store_true", dest="decode",
                      default=False,
                      help="decode files under target and create manifest")

    opts, args = parser.parse_args(input_args)

    if len(args) != 1:
        parser.error('target is missing')

    target = args[0]
    if not os.path.isdir(target):
        parser.error('target is not a directory')

    input_file = opts.input_file
    if input_file is None:
        input_file = sys.stdin
    else:
        if not os.path.isfile(input_file):
            parser.error('input file does not exist')
        input_file = open(input_file, 'r')

    return (input_file, target, opts.decode)


def main():
    (input_file, target, decode) = parse_arguments(sys.argv[1:])

    files = json.load(input_file, strict=False)

    if decode:
        manifest = open(target + '/manifest', 'w')

    count = 0
    for f in files:
        count += 1
        owner = f['owner'] if 'owner' in f else ""
        group = f['group'] if 'group' in f else ""
        mode = f['mode'] if 'mode' in f else 0440

        filepath = f['path'] if not decode else str(count)
        filepath = target + "/" + filepath

        if os.path.lexists(filepath):
            backup_file = filepath + '.bak.' + timestamp()
            os.rename(filepath, backup_file)

        parentdir = os.path.dirname(filepath)
        if not os.path.exists(parentdir):
            os.makedirs(parentdir)

        newfile = open(filepath, 'w')
        newfile.write(base64.b64decode(f['contents']))
        newfile.close()

        if decode:
            manifest.write("%s\x00%s\x00%s\x00%o\x00%s\x00" %
                           (count, owner, group, mode, f['path']))

    if decode:
        manifest.close()

    input_file.close()
    return 0

if __name__ == "__main__":
    sys.exit(main())

# vim: set sta sts=4 shiftwidth=4 sw=4 et ai :
