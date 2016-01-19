#!/usr/bin/env python
#
# Copyright (C) 2015 GRNET S.A. and individual contributors.
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

"""Get or set a configuration variable inside an INI file.

Could have used Python's ConfigParser for this,
but it breaks with sloppily-formatted Windows SYSPREP.INF
answer files.

"""

import re
import sys
import os.path
import argparse


def main():
    DESCRIPTION = "Get or set a configuration variable in a INI file"
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument("path", metavar="FILE",
                        help="Path to INI file")
    parser.add_argument("action", metavar="ACTION",
                        help="Action to perform: Must be `get' or `set'.")
    parser.add_argument("section", metavar="SECTION",
                        help="The section containing the option. If the"
                             " section does not exist, it will be created.")
    parser.add_argument("key", metavar="KEY",
                        help="The name of the variable. If it does not"
                             " exist it, will be added to the specified"
                             " section.")
    parser.add_argument("value", metavar="VALUE", nargs="?",
                        help="The value of the variable to set.",
                        default="")
    args = parser.parse_args()

    if args.action != "get" and args.action != "set":
        raise ValueError("ACTION must be `get' or `set'")
    if args.action == "set" and args.value == "":
        raise ValueError("VALUE is required if ACTION is `set'")
    update = (args.action == "set")

    section = args.section
    key = args.key
    value = args.value

    section_re = re.compile("\s*\[\s*%s\s*\]\s*" % section, re.I)
    section_start_re = re.compile("\s*\[.*", re.I)
    key_re = re.compile("\s*(%s)\s*=(.*)$" % key, re.I)

    section_found = False
    key_found = False
    with open(args.path, "r") as f:
        lines = f.readlines()

    with open(args.path if update else "/dev/null", "w") as f:
        for line in lines:
            if section_re.search(line):
                # Found matching section
                section_found = True
            elif section_found and key_re.search(line):
                # Found key inside matching section.
                # Preserve case of key and write the value.
                key_found = True
                key, val = key_re.search(line).groups()
                if not update:
                    print val.strip()
                    return 0
                f.write("%s=%s\n" % (key, value))
                continue
            elif (not key_found and section_found and
                  section_start_re.match(line)):
                # Found a new section after the matching section, but without
                # finding the key. This means that this is a new key.
                f.write("%s=%s\n" % (key, value))
            f.write(line)
        if section_found and not key_found:
                f.write("%s=%s\n" % (key, value))
        if not section_found:
            f.write("[%s]\n" % section)
            f.write("%s=%s\n" % (key, value))

    return 0


if __name__ == "__main__":
    sys.exit(main())
