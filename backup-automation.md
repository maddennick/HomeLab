# Backup Automation

The homelab uses a scheduled workflow on `Host2` to manage backups to a separate Proxmox Backup Server.

## Workflow

1. A systemd timer starts the workflow Wednesday and Sunday at 02:00 America/Chicago.
2. If PBS is off, iDRAC powers on the Dell R440. The workflow waits for network, API, and datastore readiness.
3. PVE backs up VMs 100, 101, 103, and 104, then the workflow checks the task result and verifies a fresh snapshot for each VM.
4. After verified success, PBS shuts down gracefully if this run powered it on. On failure, it stays on for troubleshooting.

The workflow completed successfully on 2026-10-07. It uses task conflict checks, a host-wide lock, readiness and task timeouts, and systemd-encrypted credentials. Credential values are not stored in this repository.

Implementation: [`../scripts/pbs-weekly-backup.py`](../scripts/pbs-weekly-backup.py), [`../systemd/`](../systemd/). Operational notes: [`../handover/backup.md`](../handover/backup.md).
