# Virtualization Handover

Last reviewed: 2026-10-07.

## Proxmox VE host

- **Node:** `Host2` (`10.0.0.99/24`)
- **Software:** Proxmox VE `9.2.20` (`pve-manager 9.2.20/49318c671b82f31e`)
- **Gateway and DNS:** `10.0.0.1` and `10.0.0.107`, respectively; checked on 2026-10-07.
- **Current state:** SSH access succeeded; the node reported five VMs.

Hardware model and firmware inventory are not recorded.

## Virtual machines

Live names, states, configured memory, and boot disk sizes from `qm list` on 2026-10-07:

| VM ID | Name | State | Configured memory | Boot disk |
|---:|---|---|---:|---:|
| 100 | `GTNH` | Running | 10,240 MiB | 100 GiB |
| 101 | `HomeServer` | Running | 4,096 MiB | 32 GiB |
| 102 | `DebianTemplate` | Stopped | 4,096 MiB | 32 GiB |
| 103 | `Valheim` | Running | 12,288 MiB | 32 GiB |
| 104 | `Dev` | Running | 4,096 MiB | 32 GiB |

VM 102 is a stopped template. The configured scheduled PBS workflow backs up VMs `100`, `101`, `103`, and `104`, excluding VM 102. This scope was confirmed in the existing backup configuration and verified by the successful 2026-10-07 run.

## PVE storage configuration

Storage IDs and types were checked with `pvesm status` on 2026-10-07:

| Storage ID | Type | State at check | Notes |
|---|---|---|---|
| `local` | Directory | Active | PVE local storage |
| `local-lvm` | LVM-thin | Active | PVE local thin pool |
| `nvme` | LVM-thin | Active | Additional thin-pool storage |
| `NonZFSHDD` | Directory | Active | Directory storage; underlying device/layout not verified |
| `tank` | ZFS pool | Active | ZFS pool reported `ONLINE` by `zpool list` |
| `pbs-backup` | PBS | Inactive | Expected while PBS is powered off after its successful backup run |

PVE storage usage and physical device mappings change and were not copied into this handover. `pbs-backup` points to server `10.0.0.100`, datastore `pbs-backup`. The PBS datastore and backup workflow are documented in [backup.md](backup.md); storage notes are in [storage.md](storage.md).

## Operational notes

- The PBS workflow is installed as systemd units on `Host2`. The source and installed unit checksums matched on 2026-10-07.
- Proxmox uses a host-wide lock and checks for active `vzdump` tasks before the workflow changes PBS power state.
- The 2026-10-07 scheduled run completed successfully, created fresh snapshots for all four in-scope guests, and shut down PBS gracefully.
- VM backup is guest-level backup through PVE `vzdump` in snapshot mode; no container guests were shown in the prior audited inventory. Recheck if the guest inventory changes.

