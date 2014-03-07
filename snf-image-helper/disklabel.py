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
import abc

from collections import namedtuple
from collections import OrderedDict

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
        fmt = "<B3sB3sLL"

        def __init__(self, raw_part):
            """Create a Partition instance"""
            (self.status,
             self.start,
             self.type,
             self.end,
             self.first_sector,
             self.sector_count
             ) = struct.unpack(self.fmt, raw_part)

        def pack(self):
            """Pack the partition values into a binary string"""
            return struct.pack(self.fmt,
                               self.status,
                               self.start,
                               self.type,
                               self.end,
                               self.first_sector,
                               self.sector_count)

        @staticmethod
        def size():
            """Returns the size of an MBR partition entry"""
            return struct.calcsize(MBR.Partition.fmt)

        def __str__(self):
            return "%02Xh %s %02Xh %s %d %d" % (self.status,
                                                self.unpack_chs(self.start),
                                                self.type,
                                                self.unpack_chs(self.end),
                                                self.first_sector,
                                                self.sector_count)

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

            assert 1 <= sector < 2**6, "Invalid sector value"
            assert 0 <= head < 2**8, "Invalid head value"
            assert 0 <= cylinder < 2**10, "Invalid cylinder value"

            byte0 = head
            byte1 = (cylinder >> 2) & 0xC0 | sector
            byte2 = cylinder & 0xff

            return struct.pack('<BBB', byte0, byte1, byte2)

    def __init__(self, block):
        """Create an MBR instance"""

        self.fmt = "<444s2x16s16s16s16s2s"
        raw_part = {}     # Offset  Length          Contents
        (self.code_area,  # 0       440(max. 446)   code area
                          # 440     2(optional)     disk signature
                          # 444     2               Usually nulls
         raw_part[0],     # 446     16              Partition 0
         raw_part[1],     # 462     16              Partition 1
         raw_part[2],     # 478     16              Partition 2
         raw_part[3],     # 494     16              Partition 3
         self.signature   # 510     2               MBR signature
         ) = struct.unpack(self.fmt, block)

        self.part = {}
        for i in range(4):
            self.part[i] = self.Partition(raw_part[i])

    def size(self):
        """Return the size of a Master Boot Record."""
        return struct.calcsize(self.fmt)

    def pack(self):
        """Pack an MBR to a binary string."""
        return struct.pack(self.fmt,
                           self.code_area,
                           self.part[0].pack(),
                           self.part[1].pack(),
                           self.part[2].pack(),
                           self.part[3].pack(),
                           self.signature)

    def __str__(self):
        """Print the MBR"""
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
                        self.disklabel = FreeBSDDisklabel(d)
                    elif ptype == 0xa6:  # OpenBSD
                        self.disklabel = OpenBSDDisklabel(d)
                    else:  # NetBSD
                        self.disklabel = NetBSDDisklabel(d)
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

        # There are cases where the CHS address changes although the LBA
        # address remains the same. For example when the BIOS is configured
        # to use a disk in LBA-Assisted translation mode, the CHS
        # representation depends on the size of the disk. When we enlarge the
        # size of the disk we may have to update the starting sector's CHS
        # address too.
        start_chs = MBR.Partition.pack_chs(*self.disklabel.lba2chs(start))
        self.mbr.part[self.part_num].start = start_chs

        end_chs = MBR.Partition.pack_chs(*self.disklabel.lba2chs(end))
        self.mbr.part[self.part_num].end = end_chs

    def enlarge_last_partition(self):
        """Enlarge the last partition to cover up all the free space"""
        self.disklabel.enlarge_last_partition()

    def get_last_partition_id(self):
        """Get the ID of the last partition"""
        return self.disklabel.get_last_partition_id()

    def get_duid(self):
        """Get the Disklabel Unique Identifier (works only for OpenBSD)"""
        if 'uid' in self.disklabel.field:
            return self.disklabel.field['uid']

        return ""

    def linux_partition_mapping(self):
        """Print the Linux kernel partition mapping"""

        offset = self.mbr.part[self.part_num].first_sector
        size = self.mbr.part[self.part_num].sector_count

        title = "BSD to Linux partition mapping"
        ret = "%s\n%s\n" % (title, "=" * len(title))

        # I peeped the kernel (linux/block/partitions/msdos.c) and this is how
        # the mapping is done
        i = 5
        for p in xrange(self.disklabel.field['npartitions']):
            bsd_start = self.disklabel.ptable.getpoffset(p)
            bsd_size = self.disklabel.ptable.getpsize(p)
            name = chr(ord('a') + p)

            if (offset == bsd_start) and (size == bsd_size):
                # full parent partition
                ret += "%c: %d\n" % (name, self.part_num + 1)
                continue

            if (offset > bsd_start) or \
                    ((offset + size) < (bsd_start + bsd_size)):
                # Bad subpartition - ignored
                continue

            ret += "%c: %d\n" % (name, i)
            i += 1
        return ret


class DisklabelBase(object):
    """Disklabel base class"""
    __metaclass__ = abc.ABCMeta

    def __init__(self, device):
        """Create a Disklabel instance"""

        # Subclasses need to overwrite this
        self.field = None
        self.ptable = None

    @abc.abstractproperty
    def fmt(self):
        """Fields format string for the disklabel fields"""
        pass

    def pack(self, checksum=None):
        """Return a binary copy of the Disklabel block"""

        if checksum is not None:
            out = self.field.copy()
            out['checksum'] = checksum
        else:
            out = self.field

        return struct.pack(self.fmt, * out.values() + [self.ptable.pack()])

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

    def write_to(self, device):
        """Write the disklabel to a device"""

        # The disklabel starts at sector 1
        device.seek(BLOCKSIZE, os.SEEK_CUR)
        device.write(self.pack())

    def lba2chs(self, lba, hpc=None, spt=None):
        """Returns the CHS address for a given LBA address"""

        assert (hpc is None) or (hpc > 0), "Invalid heads per cylinder value"
        assert (spt is None) or (spt > 0), "Invalid sectors per track value"

        if hpc is None:
            hpc = self.field['ntracks']

        if spt is None:
            spt = self.field['nsectors']

        # See:
        # http://en.wikipedia.org/wiki/Logical_Block_Addressing#CHS_conversion
        #

        cylinder = lba // (spt * hpc)
        header = (lba // spt) % hpc
        sector = (lba % spt) + 1

        return (cylinder, header, sector)

    @abc.abstractmethod
    def get_last_partition_id(self):
        """Get the ID of the last partition"""
        pass

    @abc.abstractmethod
    def __str__(self):
        """Print the Disklabel"""
        pass

    def enlarge(self, new_size):
        """Enlarge the disk and return the last useable sector"""
        raise NotImplementedError

    def enlarge_last_partition(self):
        """Enlarge the last partition to consume all the useable space"""
        raise NotImplementedError


class PartitionTableBase(object):
    """Base Class for disklabel partition tables"""
    __metaclass__ = abc.ABCMeta

    @abc.abstractproperty
    def fmt(self):
        """Partition fields format string"""
        pass

    @abc.abstractproperty
    def fields(self):
        """The partition fields"""
        pass

    @abc.abstractmethod
    def setpsize(self, i, size):
        """Set size for partition i"""
        pass

    @abc.abstractmethod
    def getpsize(self, i):
        """Get size for partition i"""
        pass

    @abc.abstractmethod
    def setpoffset(self, i, offset):
        """Set offset for partition i"""
        pass

    @abc.abstractmethod
    def getpoffset(self, i):
        """Get offset for partition i"""
        pass

    def __init__(self, ptable, pnumber):
        """Create a Partition Table instance"""

        self.Partition = namedtuple('Partition', self.fields)
        self.part = []

        size = struct.calcsize(self.fmt)
        raw = cStringIO.StringIO(ptable)
        try:
            for _ in xrange(pnumber):
                self.part.append(
                    self.Partition(*struct.unpack(self.fmt, raw.read(size)))
                    )
        finally:
            raw.close()

    def __str__(self):
        """Print the Partition table"""
        val = ""
        for i in xrange(len(self.part)):
            val += "%c: %s\n" % (chr(ord('a') + i), str(self.part[i]))
        return val

    def pack(self):
        """Packs the partition table into a binary string."""
        ret = ""
        for i in xrange(len(self.part)):
            ret += struct.pack(self.fmt, *self.part[i])
        return ret + ((364 - len(self.part) * 16) * '\x00')


class BSDDisklabel(DisklabelBase):
    """Represents a BSD Disklabel"""

    class PartitionTable(PartitionTableBase):
        """Represents a BSD Partition Table"""

        @property
        def fmt(self):
            """Partition fields format string"""
            return "<IIIBBH"

        @property
        def fields(self):
            """The partition fields"""
            return [    # Offset  Length Contents
                'size',     # 0       4      Number of sectors in partition
                'offset',   # 4       4      Starting sector of the partition
                'fsize',    # 8       4      File system basic fragment size
                'fstype',   # 12      1      File system type
                'frag',     # 13      1      File system fragments per block
                'cpg'       # 14      2      File system cylinders per group
                ]

        def setpsize(self, i, size):
            """Set size for partition i"""
            tmp = self.part[i]
            self.part[i] = self.Partition(size, tmp.offset, tmp.fsize,
                                          tmp.fstype, tmp.frag, tmp.cpg)

        def getpsize(self, i):
            """Get size for partition i"""
            return self.part[i].size

        def setpoffset(self, i, offset):
            """Set offset for partition i"""
            tmp = self.part[i]
            self.part[i] = self.Partition(tmp.size, offset, tmp.fsize,
                                          tmp.fstype, tmp.frag, tmp.cpg)

        def getpoffset(self, i):
            """Get offset for partition i"""
            return self.part[i].offset

    @property
    def fmt(self):
        return "<IHH16s16sIIIIIIHHIHHHHIII20s20sIHHII364s"

    def __init__(self, device):
        """Create a BSD DiskLabel instance"""

        super(BSDDisklabel, self).__init__(device)

        # Disklabel starts at offset one
        device.seek(BLOCKSIZE, os.SEEK_CUR)
        sector1 = device.read(BLOCKSIZE)

        d_ = OrderedDict()      # Off  Len    Content
        (d_["magic"],           # 0    4      Magic
         d_["dtype"],           # 4    2      Drive Type
         d_["subtype"],         # 6    2      Subtype
         d_["typename"],        # 8    16     Type Name
         d_["packname"],        # 24   16     Pack Identifier
         d_["secsize"],         # 32   4      Bytes per sector
         d_["nsectors"],        # 36   4      Data sectors per track
         d_["ntracks"],         # 40   4      Tracks per cylinder
         d_["ncylinders"],      # 44   4      Data cylinders per unit
         d_["secpercyl"],       # 48   4      Data sectors per cylinder
         d_["secperunit"],      # 52   4      Data sectors per unit
         d_["sparespertrack"],  # 56   2      Spare sectors per track
         d_["sparespercyl"],    # 58   2      Spare sectors per cylinder
         d_["acylinders"],      # 60   4      Alternative cylinders per unit
         d_["rpm"],             # 64   2      Rotation Speed
         d_["interleave"],      # 66   2      Hardware sector interleave
         d_["trackskew"],       # 68   2      Sector 0 skew, per track
         d_["cylskew"],         # 70   2      Sector 0 skew, per cylinder
         d_["headswitch"],      # 72   4      Head switch time
         d_["trkseek"],         # 76   4      Track-to-track seek
         d_["flags"],           # 80   4      Generic Flags
         d_["drivedata"],       # 84   5*4    Drive-type specific information
         d_["spare"],           # 104  5*4    Reserved for future use
         d_["magic2"],          # 124  4      Magic Number
         d_["checksum"],        # 128  2      Xor of data including partitions
         d_["npartitions"],     # 130  2      Number of partitions following
         d_["bbsize"],          # 132  4      size of boot area at sn0, bytes
         d_["sbsize"],          # 136  4      Max size of fs superblock, bytes
         ptable_raw             # 140  16*16  Partition Table
         ) = struct.unpack(self.fmt, sector1)

        assert d_['magic'] == d_['magic2'] == DISKMAGIC, "Disklabel not valid"
        self.ptable = self.PartitionTable(ptable_raw, d_['npartitions'])
        self.field = d_

    def enlarge(self, new_size):
        """Enlarge the disk and return the last useable sector"""
        raise NotImplementedError

    def enlarge_last_partition(self):
        raise NotImplementedError

    def get_last_partition_id(self):
        """Returns the id of the last partition"""
        end = 0

        # Exclude partition 'c' which describes the whole disk
        for i in [n for n in range(len(self.ptable.part)) if n != 2]:
            current_end = self.ptable.part[i].size + self.ptable.part[i].offset
            if end < current_end:
                end = current_end
                part = i

        assert end > 0, "No partition found"

        return part

    def __str__(self):
        """Print the Disklabel"""

        # Those fields may contain null bytes
        typename = self.field['typename'].strip('\x00').strip()
        packname = self.field['packname'].strip('\x00').strip()

        title = "Disklabel"
        return \
            "%s\n%s\n" % (title, len(title) * "=") + \
            "Magic Number: 0x%(magic)x\n" \
            "Drive type: %(dtype)d\n" \
            "Subtype: %(subtype)d\n" % self.field + \
            "Typename: %s\n" % typename + \
            "Pack Identifier: %s\n" % packname + \
            "# of bytes per sector: %(secsize)d\n" \
            "# of data sectors per track: %(nsectors)d\n" \
            "# of tracks per cylinder: %(ntracks)d\n" \
            "# of data cylinders per unit: %(ncylinders)d\n" \
            "# of data sectors per cylinder: %(secpercyl)d\n" \
            "# of data sectors per unit: %(secperunit)d\n" \
            "# of spare sectors per track: %(sparespertrack)d\n" \
            "# of spare sectors per cylinder: %(sparespercyl)d\n" \
            "Alt. cylinders per unit: %(acylinders)d\n" \
            "Rotational speed: %(rpm)d\n" \
            "Hardware sector interleave: %(interleave)d\n" \
            "Sector 0 skew, per track: %(trackskew)d\n" \
            "Sector 0 skew, per cylinder: %(cylskew)d\n" \
            "Head switch time, usec: %(headswitch)d\n" \
            "Track-to-track seek, usec: %(trkseek)d\n" \
            "Generic Flags: %(flags)r\n" \
            "Drive data: %(drivedata)r\n" \
            "Reserved for future use: %(spare)r\n" \
            "The magic number again: 0x%(magic2)x\n" \
            "Checksum: %(checksum)d\n" \
            "Number of partitions: %(npartitions)d\n"  \
            "Size of boot aread at sn0: %(bbsize)d\n"  \
            "Max size of fs superblock: %(sbsize)d\n" % self.field + \
            "%s" % self.ptable


class FreeBSDDisklabel(BSDDisklabel):
    """Represents a FreeBSD Disklabel"""
    pass


class NetBSDDisklabel(BSDDisklabel):
    """Represents a NetBSD Disklabel"""

    def lba2chs(self, lba, hpc=None, spt=None):
        """Return the CHS address for a given LBA address"""

        # NetBSD uses LBA-Assisted translation. The sectors per track (spt)
        # value is always 63 and the heads per cylinder (hpc) value depends on
        # the size of the disk

        disk_size = self.field['secperunit']

        # Maximum disk size that can be addressed is 1024 * HPC* SPT
        spt = 63
        for hpc in 16, 32, 64, 128, 255:
            if disk_size <= 1024 * hpc * spt:
                break

        chs = super(NetBSDDisklabel, self).lba2chs(lba, hpc, spt)

        if chs[0] > 1023:  # Cylinders overflowed
            assert hpc == 255  # Cylinders may overflow only for large disks
            return (1023, chs[1], chs[2])

        return chs

    def enlarge(self, new_size):
        """Enlarge the disk and return the last useable sector"""

        assert new_size >= self.field['secperunit'], \
            "New size cannot be smaller than %d" % self.field['secperunit']

        self.field['secperunit'] = new_size

        # According to the ATA specifications, "If the content of words (61:60)
        # is greater than or equal to 16,514,064 then the content of word 1
        # [the number of logical cylinders] shall be equal to 16,383."
        # NetBSD respects this.
        self.field['ncylinders'] = 16383 if new_size >= 16514064 else \
            new_size // self.field['secpercyl']

        # Partition 'c' describes the NetBSD MBR partition
        self.ptable.setpsize(2, new_size - self.ptable.getpoffset(2))

        # Partition 'd' describes the entire disk
        self.ptable.setpsize(3, new_size)

        # Update the checksum
        self.field['checksum'] = self.compute_checksum()

        return new_size - 1

    def enlarge_last_partition(self):
        """Enlarge the last partition to cover up all the free space"""

        last = self.get_last_partition_id()
        size = self.field['secperunit'] - self.ptable.part[last].offset
        self.ptable.setpsize(last, size)

        self.field['checksum'] = self.compute_checksum()

    def get_last_partition_id(self):
        """Returns the id of the last partition"""
        end = 0

        # Exclude partition 'c' which describes the NetBSD MBR partition and
        # partition 'd' which describes the whole disk
        for i in [n for n in range(len(self.ptable.part)) if n not in (2, 3)]:
            current_end = self.ptable.part[i].size + self.ptable.part[i].offset
            if end < current_end:
                end = current_end
                part = i

        assert end > 0, "No partition found"

        return part


class OpenBSDDisklabel(DisklabelBase):
    """Represents an OpenBSD Disklabel"""

    class PartitionTable(PartitionTableBase):
        """Reprepsents an OpenBSD Partition Table"""

        @property
        def fmt(self):
            return "<IIHHBBH"

        @property
        def fields(self):
            return [        # Offset  Length Contents
                'size',     # 0       4      Number of sectors in the partition
                'offset',   # 4       4      Starting sector of the partition
                'offseth',  # 8       2      Starting sector (high part)
                'sizeh',    # 10      2      Number of sectors (high part)
                'fstype',   # 12      1      File system type
                'frag',     # 13      1      File system fragments per block
                'cpg'       # 14      2      File system cylinders per group
                ]

        def setpsize(self, i, size):
            """Set size for partition i"""
            tmp = self.part[i]
            self.part[i] = self.Partition(
                size & 0xffffffff, tmp.offset, tmp.offseth, size >> 32,
                tmp.fstype, tmp.frag, tmp.cpg)

        def getpsize(self, i):
            """Get size for partition i"""
            return (self.part[i].sizeh << 32) + self.part[i].size

        def setpoffset(self, i, offset):
            """Set offset for partition i"""
            tmp = self.part[i]
            self.part[i] = self.Partition(
                tmp.size, offset & 0xffffffff, offset >> 32, tmp.sizeh,
                tmp.frag, tmp.cpg)

        def getpoffset(self, i):
            """Get offset for partition i"""
            return (self.part[i].offseth << 32) + self.part[i].offset

    @property
    def fmt(self):
        return "<IHH16s16sIIIIII8sIHHIII20sHH16sIHHII364s"

    def __init__(self, device):
        """Create a DiskLabel instance"""

        super(OpenBSDDisklabel, self).__init__(device)

        # Disklabel starts at offset one
        device.seek(BLOCKSIZE, os.SEEK_CUR)
        sector1 = device.read(BLOCKSIZE)

        d_ = OrderedDict()   # Off  Len    Content
        (d_["magic"],        # 0    4      Magic
         d_["dtype"],        # 4    2      Drive Type
         d_["subtype"],      # 6    2      Subtype
         d_["typename"],     # 8    16     Type Name
         d_["packname"],     # 24   16     Pack Identifier
         d_["secsize"],      # 32   4      Bytes per sector
         d_["nsectors"],     # 36   4      Data sectors per track
         d_["ntracks"],      # 40   4      Tracks per cylinder
         d_["ncylinders"],   # 44   4      Data cylinders per unit
         d_["secpercyl"],    # 48   4      Data sectors per cylinder
         d_["secperunit"],   # 52   4      Data sectors per unit
         d_["uid"],          # 56   8      Unique label identifier
         d_["acylinders"],   # 64   4      Alt cylinders per unit
         d_["bstarth"],      # 68   2      Start of useable region (high part)
         d_["bendh"],        # 70   2      Size of useable region (high part)
         d_["bstart"],       # 72   4      Start of useable region
         d_["bend"],         # 76   4      End of useable region
         d_["flags"],        # 80   4      Generic Flags
         d_["drivedata"],    # 84   5*4    Drive-type specific information
         d_["secperunith"],  # 104  2      Number of data sectors (high part)
         d_["version"],      # 106  2      Version
         d_["spare"],        # 108  4*4    Reserved for future use
         d_["magic2"],       # 124  4      Magic number
         d_["checksum"],     # 128  2      Xor of data including partitions
         d_["npartitions"],  # 130  2      Number of partitions in following
         d_["bbsize"],       # 132  4      size of boot area at sn0, bytes
         d_["sbsize"],       # 136  4      Max size of fs superblock, bytes
         ptable_raw          # 140  16*16  Partition Table
         ) = struct.unpack(self.fmt, sector1)

        assert d_['magic'] == d_['magic2'] == DISKMAGIC, "Disklabel not valid"
        self.ptable = self.PartitionTable(ptable_raw, d_['npartitions'])
        self.field = d_

    def setdsize(self, dsize):
        """Set disk size"""
        self.field['secperunith'] = dsize >> 32
        self.field['secperunit'] = dsize & 0xffffffff

    def getdsize(self):
        """Get disk size"""
        return (self.field['secperunith'] << 32) + self.field['secperunit']

    dsize = property(getdsize, setdsize, None, "disk size")

    def setbstart(self, bstart):
        """Set start of useable region"""
        self.field['bstarth'] = bstart >> 32
        self.field['bstart'] = bstart & 0xffffffff

    def getbstart(self):
        """Get start of useable region"""
        return (self.field['bstarth'] << 32) + self.field['bstart']

    bstart = property(getbstart, setbstart, None, "start of useable region")

    def setbend(self, bend):
        """Set end of useable region"""
        self.field['bendh'] = bend >> 32
        self.field['bend'] = bend & 0xffffffff

    def getbend(self):
        """Get end of useable region"""
        return (self.field['bendh'] << 32) + self.field['bend']

    bend = property(getbend, setbend, None, "end of useable region")

    def enlarge(self, new_size):
        """Enlarge the disk and return the last useable sector"""

        assert new_size >= self.dsize, \
            "New size cannot be smaller that %d" % self.dsize

        # Fix the disklabel
        self.dsize = new_size
        self.field['ncylinders'] = self.dsize // (self.field['nsectors'] *
                                                  self.field['ntracks'])
        self.bend = (self.field['ncylinders'] * self.field['nsectors'] *
                     self.field['ntracks'])

        # Partition 'c' describes the entire disk
        self.ptable.setpsize(2, new_size)

        # Update the checksum
        self.field['checksum'] = self.compute_checksum()

        # The last useable sector is the end of the useable region minus one
        return self.bend - 1

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

        if end > (self.bend - 1024):
            return

        self.ptable.setpsize(
            part_num, self.bend - self.ptable.getpoffset(part_num) - 1024)

        self.field['checksum'] = self.compute_checksum()

    def lba2chs(self, lba, hpc=None, spt=None):
        """Returns the CHS address for a given LBA address"""

        chs = super(OpenBSDDisklabel, self).lba2chs(lba, hpc, spt)

        # If the cylinders overflow, then OpenBSD will put the value
        #(1023, 254, 63) to the tuple.
        if chs[0] > 1023:
            return (1023, 254, 63)

        return chs

    def __str__(self):
        """Print the Disklabel"""

        # Those values may contain null bytes
        typename = self.field['typename'].strip('\x00').strip()
        packname = self.field['packname'].strip('\x00').strip()

        duid = "".join(x.encode('hex') for x in self.field['uid'])

        title = "Disklabel"
        return \
            "%s\n%s\n" % (title, len(title) * "=") + \
            "Magic Number: 0x%(magic)x\n" \
            "Drive type: %(dtype)d\n" \
            "Subtype: %(subtype)d\n" % self.field + \
            "Typename: %s\n" % typename + \
            "Pack Identifier: %s\n" % packname + \
            "# of bytes per sector: %(secsize)d\n" \
            "# of data sectors per track: %(nsectors)d\n" \
            "# of tracks per cylinder: %(ntracks)d\n" \
            "# of data cylinders per unit: %(ncylinders)d\n" \
            "# of data sectors per cylinder: %(secpercyl)d\n" \
            "# of data sectors per unit: %(secperunit)d\n" % self.field + \
            "DUID: %s\n" % duid + \
            "Alt. cylinders per unit: %(acylinders)d\n" \
            "Start of useable region (high part): %(bstarth)d\n" \
            "Size of useable region (high part): %(bendh)d\n" \
            "Start of useable region: %(bstart)d\n" \
            "End of useable region: %(bend)d\n" \
            "Generic Flags: %(flags)r\n" \
            "Drive data: %(drivedata)r\n" \
            "Number of data sectors (high part): %(secperunith)d\n" \
            "Version: %(version)d\n" \
            "Reserved for future use: %(spare)r\n" \
            "The magic number again: 0x%(magic2)x\n" \
            "Checksum: %(checksum)d\n" \
            "Number of partitions: %(npartitions)d\n"  \
            "Size of boot area at sn0: %(bbsize)d\n"  \
            "Max size of fs superblock: %(sbsize)d\n" % self.field + \
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
    parser.add_option(
        "--get-partitions-mapping", action="store_true", dest="mapping",
        default=False, help="print kernel mapping for the BSD partitions")

    options, args = parser.parse_args(sys.argv[1:])

    if len(args) != 1:
        parser.error("Wrong number of arguments")

    disk = Disk(args[0])

    if options.list:
        print disk
        return 0

    if options.duid:
        print "%s" % "".join(x.encode('hex') for x in disk.get_duid())
        return 0

    if options.mapping:
        print disk.linux_partition_mapping()
        return 0

    if options.last_part:
        print "%c" % chr(ord('a') + disk.get_last_partition_id())
        return 0

    if options.disk_size is not None:
        disk.enlarge(options.disk_size)

    if options.enlarge_partition:
        disk.enlarge_last_partition()

    disk.write()
    return 0


if __name__ == '__main__':
    sys.exit(main())

# vim: set sta sts=4 shiftwidth=4 sw=4 et ai :
