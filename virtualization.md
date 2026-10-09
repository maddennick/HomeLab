# Virtualization

Proxmox VE is the foundation of my homelab. My `Host2` node runs Proxmox VE 9.2.20 and currently hosts five virtual machines for services and other workloads.

## Platform overview

- **VM inventory:** See [Servers](servers.md) for the workloads running on the host.
- **Storage:** The host uses ZFS, LVM-thin, and directory-backed storage. See [Storage](storage.md) for details.
- **Backups:** A separate Proxmox Backup Server handles VM backups. See [Backup Automation](backup-automation.md) for how I automate the process.
