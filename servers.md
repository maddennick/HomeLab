# Server Inventory

Last reviewed: 2026-10-07. See [networking](networking.md) for address details and [virtualization](virtualization.md) for the current VM and storage inventory.

## Proxmox node

| Field | Verified detail |
|---|---|
| Hostname | `Host2` |
| Role | Proxmox VE virtualization host |
| Address | `10.0.0.99/24` |
| Proxmox VE | `9.2.20` |
| Current state | Reachable and running; checked 2026-10-07 |
| Hardware model | Not recorded; needs verification |

The node hosts VMs 100–104. See [virtualization.md](virtualization.md) for names, states, and storage. Hardware inventory, firmware, and host-specific recovery procedures have not been recorded.

## HomeServer virtual machine

| Field | Verified detail |
|---|---|
| VM ID and name | `101`, `HomeServer` |
| Address | `10.0.0.106` |
| Operating system | Debian GNU/Linux 13.5 (trixie), verified 2026-10-07; kernel version not rechecked |
| Role | Docker host for Home Assistant and Matter Server |
| Current state | VM running on 2026-10-07; SSH and Docker inventory succeeded |

Home Assistant and Matter Server containers were running at the time of the check. Their setup and maintenance notes are in [Home Assistant Docker handover](homeassistant-docker-handoff.md) and [Matter Server handover](homeassistant-matter-server-handoff.md). The `nextcloud-app` and `nextcloud-db` containers were also observed running on 2026-10-07, but their application health, persistent storage, external access, and backup arrangements have not been verified. No detailed Nextcloud handover is available yet.

## Proxmox Backup Server

| Field | Verified detail |
|---|---|
| Hostname | `backup` |
| Hardware | Dell PowerEdge R440; user-confirmed hardware RAID 10 |
| Address | `10.0.0.100` |
| Software | Proxmox Backup Server `4.2.6`, last version check 2026-09-27 |
| Out-of-band management | iDRAC named `PBS`, `10.0.0.101` |
| Current power state | Off after the successful scheduled backup and graceful shutdown on 2026-10-07 |

PBS uses datastore `pbs-backup` at `/backup`. The filesystem and RAID presentation are documented in [backup.md](backup.md); the retention settings there were last inspected on 2026-09-27. The scheduled workflow powers the server on as needed and leaves it off after verified success.

## Guest inventory

Guest names and states below are from `qm list` on 2026-10-07. Do not infer application purpose solely from a guest name.

| VM ID | Name | State |
|---:|---|---|
| 100 | `GTNH` | Running |
| 101 | `HomeServer` | Running |
| 102 | `DebianTemplate` | Stopped; template, excluded from scheduled backups |
| 103 | `Valheim` | Running |
| 104 | `Dev` | Running |
