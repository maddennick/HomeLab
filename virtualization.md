# Virtualization

`Host2` runs Proxmox VE 9.2.20 and hosts five virtual machines. The environment separates home automation, development, and other guest workloads into VMs.

## Platform overview

- VM inventory: see [server inventory](servers.md)
- Storage types: ZFS, LVM-thin, and directory-backed storage; see [storage](storage.md)
- Backup target: a separate Proxmox Backup Server; see [backup automation](backup-automation.md)

The node, guest states, and storage IDs were checked on 2026-10-07. Physical disk mappings and the ZFS vdev layout have not been audited, so no redundancy claims are made here.
