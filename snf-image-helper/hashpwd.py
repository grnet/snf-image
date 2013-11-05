#!/usr/bin/env python

# Copyright (C) 2011, 2013 GRNET S.A.
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

"""Generate a hash from a given password

This program takes a password as an argument and returns to standard output a
hash followed by a newline.

"""

import sys

import passlib.hash

from string import ascii_letters, digits
from random import choice
from os.path import basename
from optparse import OptionParser


def random_salt(length=8):
    pool = ascii_letters + digits + "/" + "."
    return ''.join(choice(pool) for i in range(length))


METHOD = {
#   Name:  (algoritm, options)
    'md5': (passlib.hash.md5_crypt, {}),
    'blowfish': (passlib.hash.bcrypt, {}),
    'sha256': (
        passlib.hash.sha256_crypt,
        {'rounds': 5000, 'implicit_rounds': True, 'salt': random_salt()}),
    'sha512': (
        passlib.hash.sha512_crypt,
        {'rounds': 5000, 'implicit_rounds': True, 'salt': random_salt()}),
    'sha1': (passlib.hash.sha1_crypt, {})
}


def parse_arguments(input_args):
    usage = "usage: %prog [-h] [-m encrypt-method] <password>"
    parser = OptionParser(usage=usage)
    parser.add_option(
        "-m", "--encrypt-method", dest="encrypt_method", type='choice',
        default="sha512", choices=METHOD.keys(),
        help="encrypt password with ENCRYPT_METHOD [%default] (supported: " +
        ", ".join(METHOD.keys()) + ")"
    )

    (opts, args) = parser.parse_args(input_args)

    if len(args) != 1:
        parser.error('password is missing')

    return (args[0], opts.encrypt_method)


def main():
    (passwd, method) = parse_arguments(sys.argv[1:])

    algorithm, options = METHOD[method]
    print algorithm.encrypt(passwd, **options)

    return 0

if __name__ == "__main__":
        sys.exit(main())

# vim: set sta sts=4 shiftwidth=4 sw=4 et ai :
