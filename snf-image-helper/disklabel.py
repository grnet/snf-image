#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 GRNET S.A.
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

"""This module provides the code for handling OpenBSD disklabels"""

import struct
import sys
import cStringIO
import optparse

from collections import namedtuple

BLOCKSIZE = 512

LABELSECTOR = 1
LABELOFFSET = 0

BBSIZE = 8192  # size of boot area with label
SBSIZE = 8192  # max size of fs superblock

DISKMAGIC = 0x82564557


class MBR(object):
    """Represents a Master Boot Record."""
    class Partition(object):
        """Represents a partition entry in MBR"""
        format = "<B3sB3sLL"

        def __init__(self, raw_part):
            """Create a Partition instance"""
            (
                self.status,
                self.start,
                self.type,
                self.end,
                self.first_sector,
                self.sector_count
            ) = struct.unpack(self.format, raw_part)

        def pack(self):
            """Pack the partition values into a binary string"""
            return struct.pack(self.format,
                               self.status,
                               self.start,
                               self.type,
                               self.end,
                               self.first_sector,
                               self.sector_count)

        @staticmethod
        def size():
            """Returns the size of an MBR partition entry"""
            return struct.calcsize(MBR.Partition.format)

        def __str__(self):
            start = self.unpack_chs(self.start)
            end = self.unpack_chs(self.end)
            return "%d %s %d %s %d %d" % (self.status, start, self.type, end,
                                          self.first_sector, self.sector_count)

        @staticmethod
        def unpack_chs(chs):
            """Unpacks a CHS address string to a tuple."""

            assert len(chs) == 3

            head = struct.unpack('<B', chs[0])[0]
            sector = struct.unpack('<B', chs[1])[0] & 0x3f
            cylinder = (struct.unpack('<B', chs[1])[0] & 0xC0) << 2 | \
                struct.unpack('<B', chs[2])[0]

            return (cylinder, head, sector)

        @staticmethod
        def pack_chs(cylinder, head, sector):
            """Packs a CHS tuple to an address string."""

            assert 1 <= sector <= 63
            assert 0 <= head <= 255
            assert 0 <= cylinder

            # If the cylinders overflow then put the value (1023, 254, 63) to
            # the tuple. At least this is what OpenBSD does.
            if cylinder > 1023:
                cylinder = 1023
                head = 254
                sector = 63

            byte0 = head
            byte1 = (cylinder >> 2) & 0xC0 | sector
            byte2 = cylinder & 0xff

            return struct.pack('<BBB', byte0, byte1, byte2)

    format = "<444s2x16s16s16s16s2s"
    """
    Offset  Length          Contents
    0       440(max. 446)   code area
    440     2(optional)     disk signature
    444     2               Usually nulls
    446     16              Partition 0
    462     16              Partition 1
    478     16              Partition 2
    494     16              Partition 3
    510     2               MBR signature
    """
    def __init__(self, block):
        """Create an MBR instance"""
        raw_part = {}
        (self.code_area,
         raw_part[0],
         raw_part[1],
         raw_part[2],
         raw_part[3],
         self.signature) = struct.unpack(self.format, block)

        self.part = {}
        for i in range(4):
            self.part[i] = self.Partition(raw_part[i])

    @staticmethod
    def size():
        """Return the size of a Master Boot Record."""
        return struct.calcsize(MBR.format)

    def pack(self):
        """Pack an MBR to a binary string."""
        return struct.pack(self.format,
                           self.code_area,
                           self.part[0].pack(),
                           self.part[1].pack(),
                           self.part[2].pack(),
                           self.part[3].pack(),
                           self.signature)

    def __str__(self):
        ret = ""
        for i in range(4):
            ret += "Partition %d: %s\n" % (i, self.part[i])
        ret += "Signature: %s %s\n" % (hex(ord(self.signature[0])),
                                       hex(ord(self.signature[1])))
        return ret


class Disklabel:
    """Represents an OpenBSD Disklabel"""
    format = "<IHH16s16sIIIIII8sIHHIII20sHH16sIHHII364s"
    """
    Offset  Length          Contents
    0       4               Magic
    4       2               Drive Type
    6       2               Subtype
    8       16              Type Name
    24      16              Pack Identifier
    32      4               Bytes per sector
    36      4               Data sectors per track
    40      4               Tracks per cilinder
    44      4               Data cylinders per unit
    48      4               Data sectors per cylynder
    52      4               Data sectors per unit
    56      8               Unique label identifier
    64      4               Alt cylinders per unit
    68      2               Start of useable region (high part)
    70      2               Size of usable region (high part)
    72      4               Start of useable region
    76      4               End of usable region
    80      4               Generic Flags
    84      5*4             Drive-type specific information
    104     2               Number of data sectors (high part)
    106     2               Version
    108     4*4             Reserved for future use
    124     4               Magic number
    128     2               Xor of data Inclu. partitions
    130     2               Number of partitions in following
    132     4               size of boot area at sn0, bytes
    136     4               Max size of fs superblock, bytes
    140     16*16           Partition Table
    """

    class PartitionTable:
        """Reprepsents an OpenBSD Partition Table"""
        format = "<IIHHBBH"
        """
        Partition Entry:
        Offset  Length          Contents
        0       4               Number of sectors in the partition
        4       4               Starting sector
        8       2               Starting sector (high part)
        10      2               Number of sectors (high part)
        12      1               Filesystem type
        13      1               Filesystem Fragment per block
        14      2               FS cylinders per group
        """

        Partition = namedtuple(
            'Partition', 'size, offset, offseth, sizeh, fstype, frag, cpg')

        def __init__(self, ptable, pnumber):
            """Create a Partition Table instance"""
            self.part = []

            size = struct.calcsize(self.format)

            raw = cStringIO.StringIO(ptable)
            try:
                for i in range(pnumber):
                    p = self.Partition(
                        *struct.unpack(self.format, raw.read(size)))
                    self.part.append(p)
            finally:
                raw.close()

        def __str__(self):
            """Print the Partition table"""
            val = ""
            for i in range(len(self.part)):
                val += "%c: %s\n" % (chr(ord('a') + i), str(self.part[i]))
            return val

        def pack(self):
            """Packs the partition table into a binary string."""
            ret = ""
            for i in range(len(self.part)):
                ret += struct.pack(self.format,
                                   self.part[i].size,
                                   self.part[i].offset,
                                   self.part[i].offseth,
                                   self.part[i].sizeh,
                                   self.part[i].fstype,
                                   self.part[i].frag,
                                   self.part[i].cpg)
            return ret

        def setpsize(self, i, size):
            """Set size for partition i"""
            tmp = self.part[i]
            self.part[i] = self.Partition(size & 0xffffffff, tmp.offset,
                                          tmp.offseth, size >> 32, tmp.fstype,
                                          tmp.frag, tmp.cpg)

        def getpsize(self, i):
            return (self.part[i].sizeh << 32) + self.part[i].size

        def setpoffset(self, i, offset):
            """Set  offset for partition i"""
            tmp = self.part[i]
            self.part[i] = self.Partition(tmp.size, offset & 0xffffffff,
                                          offset >> 32, tmp.sizeh, tmp.frag,
                                          tmp.cpg)

        def getpoffset(self, i):
            return (self.part[i].offseth << 32) + self.part[i].offset

    def __init__(self, disk):
        """Create a DiskLabel instance"""
        self.disk = disk
        self.part_num = None

        with open(disk, "rb") as d:
            sector0 = d.read(BLOCKSIZE)
            self.mbr = MBR(sector0)

            for i in range(4):
                if self.mbr.part[i].type == 0xa6:  # OpenBSD type
                    self.part_num = i
                    break

            assert self.part_num is not None, "No OpenBSD partition found"

            d.seek(BLOCKSIZE * self.mbr.part[self.part_num].first_sector)
            part_sector0 = d.read(BLOCKSIZE)
            # The offset of the disklabel from the begining of the
            # partition is one sector
            part_sector1 = d.read(BLOCKSIZE)

        (self.magic,
         self.dtype,
         self.subtype,
         self.typename,
         self.packname,
         self.secsize,
         self.nsectors,
         self.ntracks,
         self.ncylinders,
         self.secpercyl,
         self.secperunit,
         self.uid,
         self.acylinders,
         self.bstarth,
         self.bendh,
         self.bstart,
         self.bend,
         self.flags,
         self.drivedata,
         self.secperunith,
         self.version,
         self.spare,
         self.magic2,
         self.checksum,
         self.npartitions,
         self.bbsize,
         self.sbsize,
         ptable_raw) = struct.unpack(self.format, part_sector1)

        assert self.magic == DISKMAGIC, "Disklabel is not valid"

        self.ptable = self.PartitionTable(ptable_raw, self.npartitions)

    def pack(self, checksum=None):
        return struct.pack(self.format,
                           self.magic,
                           self.dtype,
                           self.subtype,
                           self.typename,
                           self.packname,
                           self.secsize,
                           self.nsectors,
                           self.ntracks,
                           self.ncylinders,
                           self.secpercyl,
                           self.secperunit,
                           self.uid,
                           self.acylinders,
                           self.bstarth,
                           self.bendh,
                           self.bstart,
                           self.bend,
                           self.flags,
                           self.drivedata,
                           self.secperunith,
                           self.version,
                           self.spare,
                           self.magic2,
                           self.checksum if checksum is None else checksum,
                           self.npartitions,
                           self.bbsize,
                           self.sbsize,
                           self.ptable.pack() +
                           ((364 - self.npartitions * 16) * '\x00'))

    def compute_checksum(self):
        """Compute the checksum of the disklabel"""

        raw = cStringIO.StringIO(self.pack(0))
        checksum = 0
        try:
            uint16 = raw.read(2)
            while uint16 != "":
                checksum ^= struct.unpack('<H', uint16)[0]
                uint16 = raw.read(2)
        finally:
            raw.close()

        return checksum

    def setdsize(self, dsize):
        """Set disk size"""
        self.secperunith = dsize >> 32
        self.secperunit = dsize & 0xffffffff

    def getdsize(self):
        """Get disk size"""
        return (self.secperunith << 32) + self.secperunit

    def setbstart(self, bstart):
        """Set start of useable region"""
        self.bstarth = bstart >> 32
        self.bstart = bstart & 0xffffffff

    def getbstart(self):
        """Get start of usable region"""
        return (self.bstarth << 32) + self.bstart

    def setbend(self, bend):
        """Set end of useable region"""
        self.bendh = bend >> 32
        self.bend = bend & 0xffffffff

    def getbend(self):
        return (self.bendh << 32) + self.bend

    def enlarge_disk(self, new_size):
        """Enlarge the size of the disk"""

        assert new_size >= self.secperunit, \
            "New size cannot be smaller that %s" % self.secperunit

        # Fix the disklabel
        self.setdsize(new_size)
        self.ncylinders = self.getdsize() // (self.nsectors * self.ntracks)
        self.setbend(self.ncylinders * self.nsectors * self.ntracks)

        # Partition 'c' descriptes the entire disk
        self.ptable.setpsize(2, new_size)

        # Fix the MBR table
        start = self.mbr.part[self.part_num].first_sector
        self.mbr.part[self.part_num].sector_count = self.getbend() - start

        lba = self.getbend() - 1
        cylinder = lba // (self.ntracks * self.nsectors)
        header = (lba // self.nsectors) % self.ntracks
        sector = (lba % self.nsectors) + 1
        chs = MBR.Partition.pack_chs(cylinder, header, sector)
        self.mbr.part[self.part_num].end = chs

        self.checksum = self.compute_checksum()

    def write(self):
        """Write the disklabel back to the media"""
        with open(self.disk, 'rw+b') as d:
            d.write(self.mbr.pack())

            d.seek((self.mbr.part[self.part_num].first_sector + 1) * BLOCKSIZE)
            d.write(self.pack())

    def get_last_partition_id(self):
        """Returns the id of the last partition"""
        part = 0
        end = 0
        # Don't check partition 'c' which is the whole disk
        for i in filter(lambda x: x != 2, range(self.npartitions)):
            curr_end = self.ptable.getpsize(i) + self.ptable.getpoffset(i)
            if end < curr_end:
                end = curr_end
                part = i

        assert end > 0, "No partition found"

        return part

    def enlarge_last_partition(self):
        """Enlarge the last partition to cover up all the free space"""

        part_num = self.get_last_partition_id()

        end = self.ptable.getpsize(part_num) + self.ptable.getpoffset(part_num)

        assert end > 0, "No partition found"

        if self.ptable.part[part_num].fstype == 1:  # Swap partition.
            #TODO: Maybe create a warning?
            return

        if end > (self.getbend() - 1024):
            return

        self.ptable.setpsize(
            part_num, self.getbend() - self.ptable.getpoffset(part_num) - 1024)

        self.checksum = self.compute_checksum()

    def __str__(self):
        """Print the Disklabel"""
        title1 = "Master Boot Record"
        title2 = "Disklabel"

        return \
            "%s\n%s\n%s\n" % (title1, len(title1) * "=", str(self.mbr)) + \
            "%s\n%s\n" % (title2, len(title2) * "=") + \
            "Magic Number: 0x%x\n" % self.magic + \
            "Drive type: %d\n" % self.dtype + \
            "Subtype: %d\n" % self.subtype + \
            "Typename: %s\n" % self.typename + \
            "Pack Identifier: %s\n" % self.packname + \
            "Number of bytes per sector: %d\n" % self.secsize + \
            "Number of data sectors per track: %d\n" % self.nsectors + \
            "Number of tracks per cylinder: %d\n" % self.ntracks + \
            "Number of data cylinders per unit: %d\n" % self.ncylinders + \
            "Number of data sectors per cylinder: %d\n" % self.secpercyl + \
            "Number of data sectors per unit: %d\n" % self.secperunit + \
            "DUID: %s\n" % "".join(x.encode('hex') for x in self.uid) + \
            "Alt. cylinders per unit: %d\n" % self.acylinders + \
            "Start of useable region (high part): %d\n" % self.bstarth + \
            "Size of useable region (high part): %d\n" % self.bendh + \
            "Start of useable region: %d\n" % self.bstart + \
            "End of usable region: %d\n" % self.bend + \
            "Generic Flags: %r\n" % self.flags + \
            "Drive data: %r\n" % self.drivedata + \
            "Number of data sectors (high part): %d\n" % self.secperunith + \
            "Version: %d\n" % self.version + \
            "Reserved for future use: %r\n" % self.spare + \
            "The magic number again: 0x%x\n" % self.magic2 + \
            "Checksum: %d\n" % self.checksum + \
            "Number of partitions: %d\n" % self.npartitions + \
            "Size of boot aread at sn0: %d\n" % self.bbsize + \
            "Max size of fs superblock: %d\n" % self.sbsize + \
            "%s" % self.ptable


if __name__ == '__main__':

    usage = "Usage: %prog [options] <input_media>"
    parser = optparse.OptionParser(usage=usage)

    parser.add_option("-l", "--list", action="store_true", dest="list",
                      default=False,
                      help="list the disklabel on the specified media")
    parser.add_option("--print-last", action="store_true", dest="last_part",
                      default=False,
                      help="print the label of the last partition")
    parser.add_option("--print-last-linux", action="store_true",
                      dest="last_linux", default=False,
                      help="print the linux number for the last partition")
    parser.add_option("--print-duid", action="store_true", dest="duid",
                      default=False,
                      help="print the disklabel unique identifier")
    parser.add_option("-d", "--enlarge-disk", type="int", dest="disk_size",
                      default=None, metavar="SIZE",
                      help="Enlarge the disk to this SIZE (in sectors)")
    parser.add_option(
        "-p", "--enlarge-partition", action="store_true",
        dest="enlarge_partition", default=False,
        help="Enlarge the last partition to cover up the free space")

    options, args = parser.parse_args(sys.argv[1:])

    if len(args) != 1:
        parser.error("Wrong number of arguments")

    disklabel = Disklabel(args[0])

    if options.list:
        print disklabel
        sys.exit(0)

    if options.duid:
        print "%s" % "".join(x.encode('hex') for x in disklabel.uid)
        sys.exit(0)

    if options.last_part:
        print "%c" % chr(ord('a') + disklabel.get_last_partition_id())

    if options.last_linux:
        part_id = disklabel.get_last_partition_id()
        # The linux kernel does not assign a partition for label 'c' that
        # describes the whole disk
        print part_id + (4 if part_id > 2 else 5)

    if options.disk_size is not None:
        disklabel.enlarge_disk(options.disk_size)

    if options.enlarge_partition:
        disklabel.enlarge_last_partition()

    disklabel.write()

sys.exit(0)

# vim: set sta sts=4 shiftwidth=4 sw=4 et ai :
