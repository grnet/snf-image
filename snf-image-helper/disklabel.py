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

"""This module provides the code for handling BSD disklabels"""

import struct
import sys
import os
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
        title = "Master Boot Record"
        return "%s\n%s\n%s\n" % (title, len(title) * "=", ret)


class Disk(object):
    """Represents a BSD Disk"""

    def __init__(self, device):
        """Create a Disk instance"""
        self.device = device
        self.part_num = None
        self.disklabel = None

        with open(device, "rb") as d:
            sector0 = d.read(BLOCKSIZE)
            self.mbr = MBR(sector0)

            for i in range(4):
                ptype = self.mbr.part[i].type
                if ptype in (0xa5, 0xa6, 0xa9):
                    d.seek(BLOCKSIZE * self.mbr.part[i].first_sector)
                    self.part_num = i
                    if ptype == 0xa5:  # FreeBSD
                        self.disklabel = BSDDisklabel(d)
                    elif ptype == 0xa6:  # OpenBSD
                        self.disklabel = OpenBSDDisklabel(d)
                    else:  # NetBSD
                        self.disklabel = BSDDisklabel(d)
                    break

        assert self.disklabel is not None, "No *BSD partition found"

    def write(self):
        """Write the changes back to the media"""
        with open(self.device, 'rw+b') as d:
            d.write(self.mbr.pack())

            d.seek(self.mbr.part[self.part_num].first_sector * BLOCKSIZE)
            self.disklabel.write_to(d)

    def __str__(self):
        """Print the partitioning info of the Disk"""
        return str(self.mbr) + str(self.disklabel)

    def enlarge(self, new_size):
        """Enlarge the disk and return the last useable sector"""

        # Fix the disklabel
        end = self.disklabel.enlarge(new_size)

        # Fix the MBR
        start = self.mbr.part[self.part_num].first_sector
        self.mbr.part[self.part_num].sector_count = end - start + 1

        cylinder = end // (self.disklabel.ntracks * self.disklabel.nsectors)
        header = (end // self.disklabel.nsectors) % self.disklabel.ntracks
        sector = (end % self.disklabel.nsectors) + 1
        chs = MBR.Partition.pack_chs(cylinder, header, sector)
        self.mbr.part[self.part_num].end = chs

    def enlarge_last_partition(self):
        self.disklabel.enlarge_last_partition()


class BSDDisklabel(object):
    """Represents a BSD Disklabel"""

    class PartitionTable:
        """Represents a BSD Partition Table"""
        format = "<IIIBBH"
        """
        Partition Entry:
        Offset  Length          Contents
        0       4               Number of sectors in partition
        4       4               Starting sector
        8       4               Filesystem basic fragment size
        12      1               Filesystem type
        13      1               Filesystem fragments per block
        14      2               Filesystem cylinders per group
        """

        Partition = namedtuple(
            'Partition', 'size, offset, fsize, fstype, frag, cpg')

    format = "<IHH16s16sIIIIIIHHIHHHHIII20s20sIHHII64s"
    """
    Offset  Length          Contents
    0       4               Magic
    4       2               Drive Type
    6       2               Subtype
    8       16              Type Name
    24      16              Pack Identifier
    32      4               Bytes per sector
    36      4               Data sectors per track
    40      4               Tracks per cylinder
    44      4               Data cylinders per unit
    48      4               Data sectors per cylinder
    52      4               Data sectors per unit
    56      2               Spare sectors per track
    58      2               Spare sectors per cylinder
    60      4               Alternative cylinders per unit
    64      2               Rotation Speed
    66      2               Hardware sector interleave
    68      2               Sector 0 skew, per track
    70      2               Sector 0 skew, per cylinder
    72      4               Head switch time
    76      4               Track-to-track seek
    80      4               Generic Flags
    84      5*4             Drive-type specific information
    104     5*4             Reserved for future use
    124     4               Magic Number
    128     2               Xor of data including partitions
    130     2               Number of partitions following
    132     4               size of boot area at sn0, bytes
    136     4               Max size of fs superblock, bytes
    140     16*16           Partition Table
    """


class OpenBSDDisklabel(object):
    """Represents an OpenBSD Disklabel"""

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
        12      1               File system type
        13      1               File system Fragment per block
        14      2               File system cylinders per group
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
            """Get size for partition i"""
            return (self.part[i].sizeh << 32) + self.part[i].size

        def setpoffset(self, i, offset):
            """Set offset for partition i"""
            tmp = self.part[i]
            self.part[i] = self.Partition(tmp.size, offset & 0xffffffff,
                                          offset >> 32, tmp.sizeh, tmp.frag,
                                          tmp.cpg)

        def getpoffset(self, i):
            """Get offset for partition i"""
            return (self.part[i].offseth << 32) + self.part[i].offset

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
    40      4               Tracks per cylinder
    44      4               Data cylinders per unit
    48      4               Data sectors per cylinder
    52      4               Data sectors per unit
    56      8               Unique label identifier
    64      4               Alt cylinders per unit
    68      2               Start of useable region (high part)
    70      2               Size of useable region (high part)
    72      4               Start of useable region
    76      4               End of useable region
    80      4               Generic Flags
    84      5*4             Drive-type specific information
    104     2               Number of data sectors (high part)
    106     2               Version
    108     4*4             Reserved for future use
    124     4               Magic number
    128     2               Xor of data including partitions
    130     2               Number of partitions in following
    132     4               size of boot area at sn0, bytes
    136     4               Max size of fs superblock, bytes
    140     16*16           Partition Table
    """
    def __init__(self, device):
        """Create a DiskLabel instance"""

        device.seek(BLOCKSIZE, os.SEEK_CUR)
        # The offset of the disklabel from the beginning of the partition is
        # one sector
        sector1 = device.read(BLOCKSIZE)

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
         ptable_raw) = struct.unpack(self.format, sector1)

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
        """Get start of useable region"""
        return (self.bstarth << 32) + self.bstart

    def setbend(self, bend):
        """Set end of useable region"""
        self.bendh = bend >> 32
        self.bend = bend & 0xffffffff

    def getbend(self):
        """Get end of useable region"""
        return (self.bendh << 32) + self.bend

    def enlarge(self, new_size):
        """Enlarge the size of the disk and return the last useable sector"""

        assert new_size >= self.getdsize(), \
            "New size cannot be smaller that %d" % self.getdsize()

        # Fix the disklabel
        self.setdsize(new_size)
        self.ncylinders = self.getdsize() // (self.nsectors * self.ntracks)
        self.setbend(self.ncylinders * self.nsectors * self.ntracks)

        # Partition 'c' describes the entire disk
        self.ptable.setpsize(2, new_size)

        # Update the checksum
        self.checksum = self.compute_checksum()

        # The last useable sector is the end of the useable region minus one
        return self.getbend() - 1

    def write_to(self, device):
        """Write the disklabel to a device"""

        # The disklabel starts at sector 1
        device.seek(BLOCKSIZE, os.SEEK_CUR)
        device.write(self.pack())

    def get_last_partition_id(self):
        """Returns the id of the last partition"""
        end = 0
        # Don't check partition 'c' which is the whole disk
        for i in [n for n in range(len(self.ptable.part)) if n != 2]:
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

        title = "Disklabel"
        return \
            "%s\n%s\n" % (title, len(title) * "=") + \
            "Magic Number: 0x%x\n" % self.magic + \
            "Drive type: %d\n" % self.dtype + \
            "Subtype: %d\n" % self.subtype + \
            "Typename: %s\n" % self.typename.strip('\x00').strip() + \
            "Pack Identifier: %s\n" % self.packname.strip('\x00').strip() + \
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
            "End of useable region: %d\n" % self.bend + \
            "Generic Flags: %r\n" % self.flags + \
            "Drive data: %r\n" % self.drivedata + \
            "Number of data sectors (high part): %d\n" % self.secperunith + \
            "Version: %d\n" % self.version + \
            "Reserved for future use: %r\n" % self.spare + \
            "The magic number again: 0x%x\n" % self.magic2 + \
            "Checksum: %d\n" % self.checksum + \
            "Number of partitions: %d\n" % self.npartitions + \
            "Size of boot area at sn0: %d\n" % self.bbsize + \
            "Max size of fs superblock: %d\n" % self.sbsize + \
            "%s" % self.ptable


def main():
    """Main entry point"""
    usage = "Usage: %prog [options] <input_media>"
    parser = optparse.OptionParser(usage=usage)

    parser.add_option("-l", "--list", action="store_true", dest="list",
                      default=False,
                      help="list the disklabel on the specified media")
    parser.add_option("--get-last-partition", action="store_true",
                      dest="last_part", default=False,
                      help="print the label of the last partition")
    parser.add_option(
        "--get-duid", action="store_true", dest="duid", default=False,
        help="print the Disklabel Unique Identifier (OpenBSD only)")
    parser.add_option("-d", "--enlarge-disk", type="int", dest="disk_size",
                      default=None, metavar="SIZE",
                      help="enlarge the disk to this SIZE (in sectors)")
    parser.add_option(
        "-p", "--enlarge-partition", action="store_true",
        dest="enlarge_partition", default=False,
        help="enlarge the last partition to cover up the free space")

    options, args = parser.parse_args(sys.argv[1:])

    if len(args) != 1:
        parser.error("Wrong number of arguments")

    disk = Disk(args[0])

    if options.list:
        print disk
        return 0

    if options.duid:
        print "%s" % "".join(x.encode('hex') for x in disk.uid)
        return 0

    if options.last_part:
        print "%c" % chr(ord('a') + disk.get_last_partition_id())

    if options.disk_size is not None:
        disk.enlarge(options.disk_size)

    if options.enlarge_partition:
        disk.enlarge_last_partition()

    disk.write()
    return 0


if __name__ == '__main__':
    sys.exit(main())

# vim: set sta sts=4 shiftwidth=4 sw=4 et ai :
