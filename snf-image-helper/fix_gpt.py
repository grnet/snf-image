#!/usr/bin/env python

# Copyright (C) 2012 GRNET S.A.
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

import struct
import sys
import binascii
import stat
import os

BLOCKSIZE = 512


class MBR(object):
    """Represents a Master Boot Record."""
    class Partition(object):
        format = "<B3sB3sLL"

        def __init__(self, raw_part):
            (
                self.status,
                self.start,
                self.type,
                self.end,
                self.first_sector,
                self.sector_count
            ) = struct.unpack(self.format, raw_part)

        def pack(self):
            return struct.pack
            (
                self.format,
                self.status,
                self.start,
                self.type,
                self.end,
                self.first_sector,
                self.sector_count
            )

        @staticmethod
        def size():
            """Returns the size of an MBR partition entry"""
            return struct.calcsize(MBR.Partition.format)

        def unpack_chs(self, chs):
            """Unpacks a CHS address string to a tuple."""

            assert len(chs) == 3

            head = struct.unpack('<B', chs[0])[0]
            sector = struct.unpack('<B', chs[1])[0] & 0x3f
            cylinder = (struct.unpack('<B', chs[1])[0] & 0xC0) << 2 | \
                struct.unpack('<B', chs[2])[0]

            return (cylinder, head, sector)

        def pack_chs(self, cylinder, head, sector):
            """Packs a CHS tuple to an address string."""

            assert 1 <= sector <= 63
            assert 0 <= cylinder <= 1023
            assert 0 <= head <= 255

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
        raw_part = {}
        self.code_area, \
            raw_part[0], \
            raw_part[1], \
            raw_part[2], \
            raw_part[3], \
            self.signature = struct.unpack(self.format, block)

        self.part = {}
        for i in range(4):
            self.part[i] = self.Partition(raw_part[i])

    @staticmethod
    def size():
        """Returns the size of a Master Boot Record."""
        return struct.calcsize(MBR.format)

    def pack(self):
        """Packs an MBR to a binary string."""
        return struct.pack(
            self.format,
            self.code_area,
            self.part[0].pack(),
            self.part[1].pack(),
            self.part[2].pack(),
            self.part[3].pack(),
            self.signature
        )


class GPTPartitionTable(object):
    """Represents a GUID Partition Table."""
    class GPTHeader(object):
        """Represents a GPT Header of a GUID Partition Table."""
        format = "<8s4sII4xQQQQ16sQIII"
        """
        Offset	Length 	        Contents
        0       8 bytes         Signature
        8       4 bytes 	Revision
        12      4 bytes 	Header size in little endian
        16 	4 bytes 	CRC32 of header
        20 	4 bytes 	Reserved; must be zero
        24 	8 bytes 	Current LBA
        32 	8 bytes 	Backup LBA
        40 	8 bytes 	First usable LBA for partitions
        48 	8 bytes 	Last usable LBA
        56 	16 bytes 	Disk GUID
        72 	8 bytes 	Partition entries starting LBA
        80 	4 bytes 	Number of partition entries
        84 	4 bytes 	Size of a partition entry
        88 	4 bytes 	CRC32 of partition array
        92 	* 	        Reserved; must be zeroes
        LBA    size            Total
        """

        def __init__(self, block):
            self.signature, \
                self.revision, \
                self.hdr_size, \
                self.header_crc32, \
                self.current_lba, \
                self.backup_lba, \
                self.first_usable_lba, \
                self.last_usable_lba, \
                self.uuid, \
                self.part_entry_start, \
                self.part_count, \
                self.part_entry_size, \
                self.part_crc32 = struct.unpack(self.format, block)

        def pack(self):
            """Packs a GPT Header to a binary string."""
            return struct.pack(
                self.format,
                self.signature,
                self.revision,
                self.hdr_size,
                self.header_crc32,
                self.current_lba,
                self.backup_lba,
                self.first_usable_lba,
                self.last_usable_lba,
                self.uuid,
                self.part_entry_start,
                self.part_count,
                self.part_entry_size,
                self.part_crc32
            )

        @staticmethod
        def size():
            """Returns the size of a GPT Header."""
            return struct.calcsize(GPTPartitionTable.GPTHeader.format)

    def __init__(self, disk):
        self.disk = disk
        with open(disk, "rb") as d:
            # MBR (Logical block address 0)
            lba0 = d.read(BLOCKSIZE)
            self.mbr = MBR(lba0)

            # Primary GPT Header (LBA 1)
            raw_header = d.read(self.GPTHeader.size())
            self.primary = self.GPTHeader(raw_header)

            # Partition entries (LBA 2...34)
            d.seek(self.primary.part_entry_start * BLOCKSIZE)
            entries_size = self.primary.part_count * \
                self.primary.part_entry_size
            self.part_entries = d.read(entries_size)

            # Secondary GPT Header (LBA -1)
            d.seek(self.primary.backup_lba * BLOCKSIZE)
            raw_header = d.read(self.GPTHeader.size())
            self.secondary = self.GPTHeader(raw_header)

    def size(self):
        """Returns the payload size of GPT partitioned device."""
        return (self.primary.backup_lba + 1) * BLOCKSIZE

    def fix(self, lba_count):
        """Move the secondary GPT Header entries to the LBA specified by
        lba_count parameter.
        """

        assert lba_count * BLOCKSIZE > self.size()

        # Correct MBR
        #TODO: Check if the partition tables is hybrid
        self.mbr.part[0].sector_count = lba_count - 1

        # Fix Primary header
        self.primary.header_crc32 = 0
        self.primary.backup_lba = lba_count - 1  # LBA-1
        self.primary.last_usable_lba = lba_count - 34  # LBA-34
        self.primary.header_crc32 = \
            binascii.crc32(self.primary.pack()) & 0xffffffff

        # Fix Secondary header
        self.secondary.header_crc32 = 0
        self.secondary.current_lba = self.primary.backup_lba
        self.secondary.last_usable_lba = lba_count - 34  # LBA-34
        self.secondary.part_entry_start = lba_count - 33  # LBA-33
        self.secondary.header_crc32 = \
            binascii.crc32(self.secondary.pack()) & 0xffffffff

        # Copy the new partition table back to the device
        with open(self.disk, "wb") as d:
            d.write(self.mbr.pack())
            d.write(self.primary.pack())
            d.write('\x00' * (BLOCKSIZE - self.primary.size()))
            d.seek(self.secondary.part_entry_start * BLOCKSIZE)
            d.write(self.part_entries)
            d.seek(self.primary.backup_lba * BLOCKSIZE)
            d.write(self.secondary.pack())
            d.write('\x00' * (BLOCKSIZE - self.secondary.size()))


if __name__ == '__main__':
    usage = "Usage: %s <disk> <sectors>\n" % (sys.argv[0])

    if len(sys.argv) != 3:
        sys.stderr.write(usage)
        sys.exit(1)

    disk = sys.argv[1]
    mode = os.stat(disk).st_mode
    if not stat.S_ISBLK(mode):
        sys.stderr.write("Parameter disk must be a block device\n")
        sys.stderr.write(usage)
        sys.exit(1)

    try:
        size = int(sys.argv[2])
    except ValueError:
        sys.stderr.write("Parameter new_size must be a number\n")
        sys.stderr.write(usage)
        sys.exit(1)

    ptable = GPTPartitionTable(disk)
    if size * BLOCKSIZE == ptable.size():
        sys.stderr.write("Nothing to do...\n")
    elif size * BLOCKSIZE > ptable.size():
        ptable.fix(size)
        sys.stderr.write("GPT table was fixed\n")
    else:
        sys.stderr.write("Disk is langer than size")
        exit(1)

    sys.exit(0)

# vim: set sta sts=4 shiftwidth=4 sw=4 et ai :
