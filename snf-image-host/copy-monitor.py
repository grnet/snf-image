#!/usr/bin/env python

# Copyright (C) 2011, 2012, 2017 GRNET S.A.
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

A small utility to monitor the progress of image deployment and produce
notifications.
"""

import os
import sys
import time
import json
import signal
import argparse
import errno
import ctypes
import ctypes.util
import fcntl
from functools import partial

MSG_TYPE = "image-copy-progress"

# From bits/fcntl-linux.h
SPLICE_F_MOVE = 1
SPLICE_F_NONBLOCK = 2
SPLICE_F_MORE = 4
SPLICE_F_GIFT = 8

# From linux/fcntl.h
F_SETPIPE_SZ = 1031


def make_splice():
    '''Set up a splice(2) wrapper'''
    # Load libc
    libc = ctypes.CDLL(ctypes.util.find_library('c'), use_errno=True)

    # Get a handle to the 'splice' call
    c_splice = libc.splice
    del libc

    c_splice.argtypes = [
        ctypes.c_int, ctypes.POINTER(ctypes.c_longlong),
        ctypes.c_int, ctypes.POINTER(ctypes.c_longlong),
        ctypes.c_size_t,
        ctypes.c_uint
    ]
    c_splice.restype = ctypes.c_ssize_t

    # pylint: disable=redefined-outer-name
    def splice(fd_in, fd_out, len_, flags):
        '''Wrapper for splice(2)

        If the call to `splice` fails (i.e. returns -1), an `OSError` is raised
        with the appropriate `errno`, unless the error is `EINTR`, which
        results in the call to be retried.
        '''

        while True:
            res = c_splice(fd_in, None, fd_out, None, len_, flags)

            if res == -1:
                errno_ = ctypes.get_errno()

                # Try again on EINTR
                if errno_ == errno.EINTR:
                    continue

                raise IOError(errno_, os.strerror(errno_))

            return res

    return splice


# Build and export wrapper
splice = make_splice()  # pylint: disable=invalid-name
del make_splice


class Progress(object):
    """Computes the progress made"""
    def __init__(self, out, interval, start, total):
        self.out = out
        self.interval = interval
        self.position = start
        self.msg = {"type": MSG_TYPE, "total": total}
        signal.signal(signal.SIGALRM, partial(self.send_progress, self))
        signal.alarm(self.interval)

    def update(self, val):
        """Update the current progress"""
        self.position += val

    def send_progress(self, *_):
        """Send progress to file descriptor"""
        self.msg['position'] = self.position
        self.msg['progress'] = float(0) if self.msg["total"] == 0 else \
            float("%2.2f" % (self.position * 100.0 / self.msg['total']))
        self.msg['timestamp'] = time.time()
        os.write(self.out, "%s\n" % json.dumps(self.msg))

        signal.alarm(self.interval)


def parse_arguments():
    """Parse input arguments"""
    description = \
        "Monitor the data passed through a pipe and periodically issue " \
        "notifications of type 'copy-progress'"

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "-b", "--buffer-size", type=int, dest="buffer_size", default=65536,
        metavar="BYTES", help="Transfer up to BYTES in every iteration")
    parser.add_argument(
        "-i", "--interval", dest="interval", default=3, type=int,
        help="The copy-progress messages creation interval")
    parser.add_argument(
        "-o", "--output_fd", type=int, dest="out", default=None, metavar="FD",
        help="Write output notifications to this file descriptor")
    parser.add_argument(
        "-s", "--start", type=int, dest="start", default=0,
        help="The number of bytes already transferred")
    parser.add_argument(
        "-t", "--total", type=int, dest="total", default=None, metavar="TOTAL",
        help="The overall number of bytes expected to be transferred")

    args = parser.parse_args()

    if args.total is None:
        sys.stderr.write("Fatal: Option '-t' is mandatory.\n")
        parser.print_help()
        sys.exit(1)

    if args.out is None:
        sys.stderr.write("Fatal: Option '-o' is mandatory.\n")
        parser.print_help()
        sys.exit(1)

    return args


def main():
    """ module entry point"""
    args = parse_arguments()

    if os.isatty(sys.stdin.fileno()):
        sys.stderr.write("Input is a tty. Expecting a pipe!\n")
        return 2

    if os.isatty(sys.stdout.fileno()):
        sys.stderr.write("Output is a tty. Expecting a pipe!\n")
        return 2

    with open('/proc/sys/fs/pipe-max-size') as pipe_max_size:
        max_size = pipe_max_size.read()

    if max_size < args.buffer_size:
        args.buffer_size = max_size

    # Make the pipe size equal to the chunk size
    fcntl.fcntl(sys.stdin.fileno(), F_SETPIPE_SZ, args.buffer_size)
    fcntl.fcntl(sys.stdout.fileno(), F_SETPIPE_SZ, args.buffer_size)

    progress = Progress(args.out, args.interval, args.start, args.total)

    while True:
        sent = splice(sys.stdin.fileno(), sys.stdout.fileno(),
                      args.buffer_size, SPLICE_F_MOVE)
        if sent < 0:
            return 3
        elif sent == 0:
            break
        else:
            progress.update(sent)

    progress.send_progress()
    return 0


if __name__ == "__main__":
    sys.exit(main())

# vim: set sta sts=4 shiftwidth=4 sw=4 et ai :
