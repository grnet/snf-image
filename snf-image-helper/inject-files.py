#!/usr/bin/env python

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
                        action="store",type='string', dest="input_file",
                        help="get input from FILE instead of stdin",
                        metavar="FILE")

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
        input_file = open(input_file,'r')
        
    return (input_file, target)


def main():
    (input_file, target) = parse_arguments(sys.argv[1:])

    files = json.loads(input_file.read())
    for f in files:
        real_path = target + '/' + f['path']
        if os.path.lexists(real_path):
            backup_file = real_path + '.bak.' + timestamp()
            os.rename(real_path, backup_file)

        parentdir = os.path.dirname(real_path)
        if not os.path.exists(parentdir):
            os.makedirs(parentdir)

        newfile = open(real_path, 'w')
        newfile.write(base64.b64decode(f['contents']))
        newfile.close()
        os.chmod(real_path, 0440)
    sys.stderr.write('Successful personalization of Image\n')

    input_file.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())

# vim: set sta sts=4 shiftwidth=4 sw=4 et ai :
