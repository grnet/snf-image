#!/usr/bin/env python

# Copyright (C) 2011, 2012 GRNET S.A.
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

"""Utility to monitor the progress of image deployment

A small utility to monitor the progress of image deployment
by watching the contents of /proc/<pid>/io and producing
notifications.
"""

import os
import sys
import time
import json
import prctl
import signal
import socket


def parse_arguments(args):
    from optparse import OptionParser

    kw = {}
    kw['usage'] = "%prog [options] command [args...]"
    kw['description'] = \
        "%prog runs 'command' with the specified arguments, monitoring the " \
        "number of bytes read by it. 'command' is assumed to be " \
        "A program used to install the OS for a Ganeti instance. %prog " \
        "periodically issues notifications of type 'copy-progress'."

    parser = OptionParser(**kw)
    parser.disable_interspersed_args()
    parser.add_option("-r", "--read-bytes",
                      action="store", type="int", dest="read_bytes",
                      metavar="BYTES_TO_READ",
                      help="The expected number of bytes to be read, " \
                           "used to compute input progress",
                      default=None)
    parser.add_option("-o", "--output_fd", dest="output", default=None,
                    metavar="FILE", type="int",
                    help="Write output notifications to this file descriptor")

    (opts, args) = parser.parse_args(args)

    if opts.read_bytes is None:
        sys.stderr.write("Fatal: Option '-r' is mandatory.\n")
        parser.print_help()
        sys.exit(1)

    if opts.output is None:
        sys.stderr.write("Fatal: Option '-o' is mandatory.\n")
        parser.print_help()
        sys.exit(1)

    if len(args) == 0:
        sys.stderr.write("Fatal: You need to specify the command to run.\n")
        parser.print_help()
        sys.exit(1)

    return (opts, args)


def report_wait_status(pid, status):
    if os.WIFEXITED(status):
        sys.stderr.write("Child PID = %d exited, status = %d\n" %
                         (pid, os.WEXITSTATUS(status)))
    elif os.WIFSIGNALED(status):
        sys.stderr.write("Child PID = %d died by signal, signal = %d\n" %
                         (pid, os.WTERMSIG(status)))
    elif os.WIFSTOPPED(status):
        sys.stderr.write("Child PID = %d stopped by signal, signal = %d\n" %
                         (pid, os.WSTOPSIG(status)))
    else:
        sys.stderr.write("Internal error: Unhandled case, " \
                         "PID = %d, status = %d\n" % (pid, status))
        sys.exit(1)
    sys.stderr.flush()


def send_message(to, message):
    message['timestamp'] = time.time()
    os.write(to, "%s\n" % json.dumps(message))


def main():
    (opts, args) = parse_arguments(sys.argv[1:])
    out = opts.output
    pid = os.fork()
    if pid == 0:
        # In child process:

        # Make sure we die with the parent and are not left behind
        # WARNING: This uses the prctl(2) call and is Linux-specific.
        prctl.set_pdeathsig(signal.SIGHUP)

        # exec command specified in arguments,
        # searching the $PATH, keeping all environment
        os.execvpe(args[0], args, os.environ)
        sys.stderr.write("execvpe failed, exiting with non-zero status")
        os.exit(1)

    # In parent process:
    iofname = "/proc/%d/io" % pid
    iof = open(iofname, "r", 0)   # 0: unbuffered open
    sys.stderr.write("%s: created child PID = %d, monitoring file %s\n" %
                     (sys.argv[0], pid, iofname))

    message = {}
    message['type'] = 'copy-progress'
    message['total'] = opts.read_bytes

    while True:
        # check if the child process is still alive
        (wpid, status) = os.waitpid(pid, os.WNOHANG)
        if wpid == pid:
            report_wait_status(pid, status)
            if (os.WIFEXITED(status) or os.WIFSIGNALED(status)):
                if not (os.WIFEXITED(status) and
                                            os.WEXITSTATUS(status) == 0):
                    return 1
                else:
                    message['position'] = message['total']
                    message['progress'] = float(100)
                    send_message(out, message)
                    return 0

        iof.seek(0)
        for l in iof.readlines():
            if l.startswith("rchar:"):
                message['position'] = int(l.split(': ')[1])
                message['progress'] = float(100) if opts.read_bytes == 0 \
                    else float("%2.2f" % (
                        message['position'] * 100.0 / message['total']))
                send_message(out, message)
                break

        # Sleep for a while
        time.sleep(3)

if __name__ == "__main__":
    sys.exit(main())

# vim: set sta sts=4 shiftwidth=4 sw=4 et ai :
