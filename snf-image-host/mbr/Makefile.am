osname=snf-image
osdir=$(OS_DIR)/$(osname)

export osdir
OBJCOPY = objcopy

dist_os_DATA = $(srcdir)/mbr.bin

mbr.elf: mbr.o
	$(LD)  -m elf_i386  -T $(srcdir)/mbr.ld -e _start -o mbr.elf mbr.o

mbr.o: mbr.S
	$(CC)  -m32 -march=i386 -mpreferred-stack-boundary=2 -mincoming-stack-boundary=2 -ffreestanding -fno-stack-protector -fwrapv -freg-struct-return -Os -fomit-frame-pointer -mregparm=3 -DREGPARM=3 -msoft-float -fno-exceptions -fno-asynchronous-unwind-tables -fno-strict-aliasing -falign-functions=0 -falign-jumps=0 -falign-labels=0 -falign-loops=0 -fvisibility=hidden -g -W -Wall -Wstrict-prototypes  -Wno-sign-compare   -D__ASSEMBLY__ -Wa,-a=$(srcdir)/mbr.lst -c -o mbr.o mbr.S

mbr.bin: mbr.elf
	$(OBJCOPY) -O binary mbr.elf mbr.bin
	$(srcdir)/pad.py mbr.bin

CLEANFILES = $(srcdir)/mbr.o $(srcdir)/mbr.elf $(srcdir)/mbr.bin $(srcdir)/mbr.lst
