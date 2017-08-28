#!/usr/bin/env python

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

"""Decode a JSON encoded string with properties

This program decodes a JSON encoded properties string and outputs it in a
bash sourceable way. The properties are passed to the program through a JSON
string either read from a file or from standard input and are outputted to a
target file.
"""

import sys
import os
import subprocess
import json
from StringIO import StringIO
from optparse import OptionParser


def parse_arguments(input_args):
    usage = "Usage: %prog [options] <output_file>"
    parser = OptionParser(usage=usage)
    parser.add_option("-i", "--input",
                      action="store", type='string', dest="input_file",
                      help="get input from FILE instead of stdin",
                      metavar="FILE")

    opts, args = parser.parse_args(input_args)

    if len(args) != 1:
        parser.error('output file is missing')
    output_file = args[0]

    if opts.input_file is not None:
        if not os.path.isfile(opts.input_file):
            parser.error('input file does not exist')

    return (opts.input_file, output_file)


def main():
    (input_file, output_file) = parse_arguments(sys.argv[1:])

    infh = sys.stdin if input_file is None else open(input_file, 'r')
    outfh = open(output_file, 'w')

    properties = json.load(infh, strict=False)
    for key, value in properties.items():
        os.environ['SNF_IMAGE_PROPERTY_' + str(key).upper()] = str(value)

    p = subprocess.Popen(['bash', '-c', 'set'], stdout=subprocess.PIPE)
    output = StringIO(p.communicate()[0])
    for line in iter(output):
        if line.startswith('SNF_IMAGE_PROPERTY_'):
            outfh.write('export ' + line)

    infh.close()
    outfh.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())

# vim: set sta sts=4 shiftwidth=4 sw=4 et ai :
