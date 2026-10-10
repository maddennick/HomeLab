# Backup Automation

My Proxmox Backup Server runs on a Dell PowerEdge R440, an enterprise server that generates quite a bit of heat and fan noise. I wanted to avoid leaving it running when it wasn't needed, so I built an automated workflow to power it on for backups and shut it down when they're finished.

## How it works

1. A systemd timer starts the workflow Wednesday and Sunday at 02:00 America/Chicago.
2. If PBS is powered off, the script turns on the Dell R440 through iDRAC and waits for the network, API, and datastore to become available.
3. Proxmox backs up VMs 100, 101, 103, and 104. The script checks the backup task and verifies that each VM has a fresh snapshot.
4. After successful verification, PBS shuts down gracefully if the workflow powered it on. If something fails, the server stays on for troubleshooting.

The script also prevents overlapping runs, checks for conflicting backup tasks, and uses timeouts to avoid waiting indefinitely. Credentials are supplied through systemd's encrypted credential mechanism rather than stored in the repository.

## Implementation

The workflow is written in Python and runs on the Proxmox VE host, with systemd handling scheduled execution.

- [View the backup automation script](scripts/pbs-weekly-backup.py)

The workflow completed a successful live run on October 7, 2026.

On October 10, 2026, I restored the GTNH server from a PBS snapshot to a new VM (ID 105) and verified SSH access. This confirmed that the backup could be restored without overwriting the original VM.

## Development notes

I used Codex to help write and refine the Python script. I focused on the problem I wanted to solve, how the workflow should behave, and the safeguards needed to avoid leaving backups incomplete or shutting down the server after a failure. I then tested the workflow in my own environment and refined it along the way.

This project was a good opportunity to use AI-assisted development to build something practical for my homelab while learning more about automation, error handling, and backup verification.
