# Homelab Infrastructure

This repository documents a Proxmox-based homelab and selected systems administration work across virtualization, self-hosted services, backup operations, and home automation.

## Highlights

- **Virtualization:** Proxmox VE hosts several Linux and application VMs.
- **Backup operations:** A systemd workflow on Proxmox starts a separate Proxmox Backup Server through iDRAC, runs VM backups, verifies the resulting snapshots, and shuts the server down after success. On failure, it leaves the server available for troubleshooting.
- **Home automation:** Home Assistant and Matter Server run in Docker on a dedicated VM.

The backup workflow completed successfully in a live run on 2026-10-07. Its source is in [`scripts/`](scripts/), with the scheduled and manual systemd units in [`systemd/`](systemd/).

Operational notes are in [`handover/`](handover/). They record implementation details and history; service state can change over time.
