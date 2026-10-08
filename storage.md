# Storage Handover

Last reviewed: 2026-10-07.

## Proxmox storage

The current storage IDs and types on `Host2` were verified with `pvesm status`:

| Storage ID | PVE storage type | State on 2026-10-07 | Known purpose/details |
|---|---|---|---|
| `local` | `dir` | Active | Local directory storage |
| `local-lvm` | `lvmthin` | Active | Local LVM-thin storage |
| `nvme` | `lvmthin` | Active | Additional LVM-thin storage; physical mapping not verified |
| `NonZFSHDD` | `dir` | Active | Directory storage; backing device and mount configuration need verification |
| `tank` | `zfspool` | Active | ZFS pool `tank`; `zpool list` reported `ONLINE` |
| `pbs-backup` | `pbs` | Inactive | Remote PBS datastore; expected inactive while PBS is shut down |

PVE also reported ZFS datasets `tank/data` and VM volumes under `tank`. The physical disk layout, redundancy, and dataset properties have not been audited. Do not infer that the ZFS pool is redundant from its name or current health state.

## Proxmox Backup Server datastore

- PBS datastore ID: `pbs-backup`
- PBS host: `backup`, `10.0.0.100`
- Datastore path: `/backup`
- PVE storage ID: `pbs-backup`
- Server: Dell PowerEdge R440 with user-confirmed hardware RAID 10
- Last observed PBS filesystem: ext4 on an LVM virtual block device; `/backup` is a directory on that filesystem (verified 2026-09-27)

The backup workflow powers the PBS host on for scheduled backups and gracefully powers it off after a successful run when it was started by that run. Full configuration and retention details are in [backup.md](backup.md).

## Items to verify

- Identify the physical devices and mount configuration backing `NonZFSHDD` and `nvme`.
- Record the `tank` vdev topology and relevant dataset properties before making claims about redundancy or recovery.
- Review current PBS datastore capacity and prune/garbage-collection schedules while PBS is powered on.

