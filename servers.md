# Server Inventory

A quick overview of the physical systems and virtual machines that make up my homelab.

## Physical Systems and Services

| System | Purpose | Details |
|---|---|---|
| `Host2` | Proxmox VE host | Runs Proxmox VE 9.2.20 and hosts five VMs. |
| `backup` | Backup server | Dell PowerEdge R440 running Proxmox Backup Server. |
| iDRAC | Remote management | Used to power the backup server on and off for automated backups. |
| `HomeServer` | Home automation | Debian 13 VM running Home Assistant and Matter Server. |

## Virtual Machines

| VM ID | Name | Purpose / State |
|---:|---|---|
| 100 | GTNH | Running game server |
| 101 | HomeServer | Running home automation services |
| 102 | DebianTemplate | Stopped; used as a VM template |
| 103 | Valheim | Running game server |
| 104 | Dev | Running development VM |

The backup workflow covers VMs 100, 101, 103, and 104. The Debian template is excluded.

See [Virtualization](virtualization.md) for the Proxmox overview, [Storage](storage.md) for the storage layout, and [Backup Automation](backup-automation.md) for how the backup process works.
