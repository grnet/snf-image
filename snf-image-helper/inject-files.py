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

This program injects files into a target directory or creates a cloud-init
configuration for the cc_write_files module. The files are passed to the
program through a JSON string either read from a file or from standard input.

"""

import sys
import os
import json
import datetime
import base64
import argparse
import yaml


def timestamp():
    now = datetime.datetime.now()
    current_time = now.strftime("%Y%m%d.%H%M%S")
    return current_time


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--target", dest="target", metavar="DIRECTORY",
                        help="write files to DIRECTORY")
    parser.add_argument("-i", "--input", dest="input_file", metavar="FILE",
                        help="get input from FILE instead of stdin")
    parser.add_argument("-d", "--decode", action="store_true", dest="decode",
                        default=False,
                        help="decode files under target and create manifest")
    parser.add_argument("-c", "--cloud-init", default=False, dest="cloudinit",
                        action="store_true",
                        help="decode files to a cloud-init configuration")

    args = parser.parse_args()

    if not args.target and not args.cloudinit:
        parser.error('Either -t or -c must be defined!')

    if args.target and args.cloudinit:
        parser.error('Options -t and -c are mutual exclusive')

    if args.target is not None and not os.path.isdir(args.target):
        parser.error('Defined target: %s is not a directory' % args.target)

    if args.input_file is not None and not os.path.isfile(args.input_file):
        parser.error('input file does not exist')

    return args


def main():
    args = parse_arguments()

    input_stream = open(args.input_file, 'r') if args.input_file else sys.stdin
    files = json.load(input_stream, strict=False)

    if args.cloudinit:
        out = {}
        out['write_files'] = []
        for f in files:
            out['write_files'].append(
                {'owner': str("%s:%s" % (f.get('owner', 'root'),
                                         f.get('group', 'root'))),
                 'permissions': f.get('mode', 0440),
                 'content': str(f['contents']),
                 'encoding': str('b64'),
                 'path': str(f['path'])})
        print yaml.dump(out, default_flow_style=False)
        return 0

    if args.decode:
        manifest = open(args.target + '/manifest', 'w')

    count = 0
    for f in files:
        count += 1
        owner = f['owner'] if 'owner' in f else ""
        group = f['group'] if 'group' in f else ""
        mode = f['mode'] if 'mode' in f else 0440

        filepath = f['path'] if not args.decode else str(count)
        filepath = args.target + "/" + filepath

        if os.path.lexists(filepath):
            backup_file = filepath + '.bak.' + timestamp()
            os.rename(filepath, backup_file)

        parentdir = os.path.dirname(filepath)
        if not os.path.exists(parentdir):
            os.makedirs(parentdir)

        newfile = open(filepath, 'w')
        newfile.write(base64.b64decode(f['contents']))
        newfile.close()

        if args.decode:
            manifest.write("%s\x00%s\x00%s\x00%o\x00%s\x00" %
                           (count, owner, group, mode, f['path']))

    if args.decode:
        manifest.close()

    input_stream.close()
    return 0

if __name__ == "__main__":
    sys.exit(main())

# vim: set sta sts=4 shiftwidth=4 sw=4 et ai :
