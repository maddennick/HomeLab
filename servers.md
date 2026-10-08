# Server Inventory

High-level inventory of the systems relevant to this portfolio.

| System | Role | Verified details |
|---|---|---|
| `Host2` | Proxmox VE host | PVE 9.2.20; hosts five VMs |
| `backup` | Proxmox Backup Server | Dell PowerEdge R440; PBS 4.2.6 last checked 2026-09-27 |
| iDRAC | Out-of-band management | Controls PBS power for the backup workflow |
| `HomeServer` | Home automation and Linux services | Debian GNU/Linux 13.5 VM running Home Assistant and Matter Server |

## Virtual machines

Guest names and states were checked on 2026-10-07.

| ID | Name | State |
|---:|---|---|
| 100 | GTNH | Running |
| 101 | HomeServer | Running |
| 102 | DebianTemplate | Stopped template |
| 103 | Valheim | Running |
| 104 | Dev | Running |

The scheduled backup workflow covers VMs 100, 101, 103, and 104. The template is excluded.
