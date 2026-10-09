# Home Automation

Home Assistant runs in Docker on my dedicated Debian VM, `HomeServer` (VM 101), hosted on Proxmox. I use it to manage smart home devices, build automations, and experiment with integrations.

## How it's set up

- **Home Assistant:** The central hub for device integrations, automations, and notifications.
- **Zigbee:** My primary focus for connecting smart home devices. I use a USB coordinator and have been expanding the network with Zigbee smart plugs to improve coverage and reliability.
- **Matter Server:** Runs as a separate Docker container alongside Home Assistant.
- **Docker Compose:** Manages the services on the Debian VM, with configuration and application data persisted on the VM.

## Ongoing work

I've been working on improving Zigbee network reliability and expanding device coverage around my apartment. This includes adding smart plugs to strengthen the mesh and troubleshooting devices that don't reliably connect.

I also use this setup to experiment with Home Assistant integrations and remote access while keeping the services hosted locally in my homelab.
