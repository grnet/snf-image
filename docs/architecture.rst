Architecture
============

snf-image is split in two components: The main program running on the Ganeti
host, with full root privilege (*snf-image* previously *snf-image-host*), and a
part running inside an unprivileged, helper VM (*snf-image-helper*).

snf-image
^^^^^^^^^

This part implements the Ganeti OS interface. It extracts the Image onto the
Ganeti-provided block device, using streaming block I/O (dd with oflag=direct),
then passes control to snf-image-helper running inside a helper VM. The helper
VM is created using KVM, runs as an unprivileged user, nobody by default.

There is no restriction on the distribution running inside the helper VM, as
long as it executes the snf-image-helper component automatically upon bootup.
The snf-image-update-helper script is provided with snf-image to automate the
creation of a helper VM image based on Debian Stable, using multistrap.

The snf-image-helper component is spawned inside a specific hardware
environment:

 * The VM features a virtual floppy, containing an ext2 filesystem with all
   parameters needed for image customization.
 * The hard disk of the VM being deployed is accessible as the first virtio
   hard disk.
 * All kernel/console output is redirected to the first virtual serial console,
   and eventually finds its way into the OS definition log files that Ganeti
   maintains.
 * The helper VM is expected to output "SUCCESS" to its second serial port if
   image customization was successful inside the VM.
 * In any other case, execution of the helper VM or snf-image-helper has
   failed.
 * The helper VM is expected to shutdown automatically once it is done. Its
   execution is time-limited; if it has not terminated after a number of
   seconds, configurable via /etc/default/snf-image, it is sent a SIGTERM
   and/or a SIGKILL.

KVM is currently a dependency for snf-image, meaning it is needed to spawn the
helper VM. There is no restriction on the hypervisor used for the actual Ganeti
instances. This is not a strict requirement; KVM could be replaced by qemu,
doing full CPU virtualization without any kernel support for spawning the
helper VM.

snf-image-helper
^^^^^^^^^^^^^^^^

This part runs inside the helper VM and undertakes customization of the VM
being deployed using a number of hooks, or tasks. The tasks run in an
environment, specified by rules found in a virtual floppy, placed there by
*snf-image*. *snf-image-helper* uses runparts to run tasks found under
*/usr/lib/snf-image-helper/tasks* by default

Graphical Representation
^^^^^^^^^^^^^^^^^^^^^^^^

The architecture is presented below:

.. image:: /images/arch.png


