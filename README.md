# Homelab Infrastructure

This is where I document the homelab I've been building and the projects I've worked on along the way. It runs on Proxmox VE and gives me a place to work with virtualization, Linux, self-hosted services, storage, and infrastructure automation outside of work. One of my main projects is automating my backup workflow, including remotely powering on my backup server, verifying snapshots, and shutting it down when the job completes successfully.

## What I'm working with

- **Virtualization:** Proxmox VE and Debian virtual machines
- **Backups:** Proxmox Backup Server with automated power management and backup verification
- **Self-hosted services:** Docker, Home Assistant, Nextcloud, and Matter Server
- **Automation:** Bash/Python scripts and systemd services

## Projects

- [Virtualization](virtualization.md) — Proxmox, virtual machines, and the templates I've built.
- [Storage](storage.md) — Storage configuration and backup infrastructure.
- [Backup Automation](backup-automation.md) — Automating the backup process, from powering on the backup server to verifying snapshots and handling failures.
- [Home Automation](home-automation.md) — Home Assistant, Docker, and Matter.
- [Servers](servers.md) — The game servers and other services I run and maintain.

I use this repository to keep track of how things are configured, why I made certain decisions, and what I've learned when things don't go as planned. It's an ongoing project, so the documentation will grow as the homelab does.
