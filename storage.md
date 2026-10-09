# Storage Overview

Storage in my homelab is split between my custom-built Proxmox host and a dedicated Dell PowerEdge R440 running Proxmox Backup Server.

## Proxmox Host

My custom-built server runs Proxmox VE and uses three local storage resources:

- **`tank`** — ZFS pool on the Proxmox host.
- **`nvme`** — Fast local storage for workloads that benefit from NVMe performance.
- **`NonZFSHDD`** — Additional HDD storage, currently unused.

These resources are part of the virtualization host and are separate from the backup server.

## Backup Server

The Dell PowerEdge R440 runs Proxmox Backup Server and provides dedicated storage for VM backups.

- **Datastore:** `pbs-backup`
- **Filesystem:** ext4
- **Mount point:** `/backup`
- **Underlying storage:** LVM virtual block device, with a hardware RAID 10 controller reported on the server.

See [Backup Automation](backup-automation.md) for how the backup server is powered on, used for backups, and shut down after successful completion.
