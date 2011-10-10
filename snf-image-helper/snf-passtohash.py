#!/usr/bin/env python
#
# Copyright (c) 2011 Greek Research and Technology Network
#
"""Generate a hash from a given password

This program takes a password as an argument and
returns to standard output a hash followed by a newline.
To do this, it generates a random salt internally.

"""

import sys
import crypt 

from string import ascii_letters, digits
from random import choice
from os.path import basename
from optparse import OptionParser


# This dictionary maps the hashing algorithm method
# with its <ID> as documented in:
# http://www.akkadia.org/drepper/SHA-crypt.txt
HASH_ID_FROM_METHOD = {
    'md5': '1',
    'blowfish': '2a',
    'sun-md5': 'md5',
    'sha256': '5',
    'sha512': '6'
}

def random_salt(length=8):
    pool = ascii_letters + digits + "/" + "."
    return ''.join(choice(pool) for i in range(length))


def parse_arguments(input_args):
    usage = "usage: %prog [-h] [-m encrypt-method] <password>"
    parser = OptionParser(usage=usage)
    parser.add_option("-m", "--encrypt-method",
			dest="encrypt_method",
			type='choice',
			default="sha512",
			choices=HASH_ID_FROM_METHOD.keys(),
			help="encrypt password with ENCRYPT_METHOD [%default] \
			(supported: " + ", ".join(HASH_ID_FROM_METHOD.keys()) +")",
    )

    (opts, args) = parser.parse_args(input_args)

    if len(args) != 1:
	parser.error('password is missing')

    return (args[0], opts.encrypt_method)


def main():
    (password, method) = parse_arguments(sys.argv[1:])
    salt = random_salt()
    hash = crypt.crypt(password, "$"+HASH_ID_FROM_METHOD[method]+"$"+salt)
    sys.stdout.write("%s\n" % (hash))
    return 0

if __name__ == "__main__":
        sys.exit(main())

# vim: set sta sts=4 shiftwidth=4 sw=4 et ai :
