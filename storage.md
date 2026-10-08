# Storage Overview

Proxmox uses multiple storage types to support virtual machine disks and local data:

- **ZFS:** pool `tank`, reported online during the 2026-10-07 review.
- **LVM-thin:** local pools named `local-lvm` and `nvme`.
- **Directory storage:** `local` and `NonZFSHDD`.
- **Backup storage:** remote PBS datastore `pbs-backup` on the Dell R440.

The R440 uses a user-confirmed hardware RAID 10 controller. PBS previously reported an ext4 filesystem on an LVM virtual block device, with its datastore under `/backup` (verified 2026-09-27).

The physical disk layout behind Proxmox storage and the ZFS vdev topology are not documented. Pool health alone does not establish redundancy.
