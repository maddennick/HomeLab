# Planned Network Overhaul

My current home network works, but I want more control over routing, security, and network segmentation. This project is about moving toward a more flexible setup that gives me hands-on experience with firewalls, managed switching, VLANs, and Wi-Fi 7.

**Status:** Planning

## Goals

- Replace the Xfinity gateway's routing responsibilities with a dedicated firewall.
- Segment devices into VLANs to improve security and control traffic between networks.
- Upgrade to managed switching and Wi-Fi 7.
- Improve visibility into network traffic and simplify ongoing management.
- Build a network that can grow alongside the rest of my homelab, including a second Proxmox node.

## Planned Architecture

The current plan is to put the Xfinity gateway into bridge mode and use OPNsense as the primary router and firewall.

The intended layout is:

1. **Xfinity gateway:** Provides the internet connection in bridge mode.
2. **OPNsense:** Handles routing, firewall rules, DHCP, and inter-VLAN traffic. Dedicated hardware is still under consideration.
3. **Managed switch:** Connects the homelab and network devices, with planned 10Gb connections to the Proxmox hosts.
4. **Wi-Fi 7 access point:** Provides wireless connectivity, with the UniFi U7 Pro currently under consideration.
5. **VLANs:** Separate network segments for different device types and purposes.

These components and their configuration are still being evaluated and have not been fully deployed.

## Planned Network Segmentation

The goal is to separate devices based on their purpose rather than keep everything on one network.

- **Management:** Infrastructure administration, including Proxmox and network equipment.
- **Servers:** Homelab services and virtual machines.
- **Trusted devices:** Personal computers and phones.
- **IoT:** Smart home devices and other less-trusted connected devices.
- **Guest:** Internet access for visitors without access to internal resources.

The final VLAN IDs, IP ranges, and firewall rules have not been decided yet.

## Proxmox Expansion

I'm also considering adding a second Proxmox node to make maintenance and recovery easier. The goal isn't necessarily automatic high availability, but having another host available when the primary node needs maintenance or experiences a failure.

With 10Gb networking between the hosts, I could move workloads during planned maintenance and restore or start important VMs on the second node if the primary host goes down.

The exact migration and storage setup still needs to be decided. Local storage, replication, and shared storage have different tradeoffs, and a second node alone doesn't guarantee that every VM can be brought up immediately.

## Hardware and Design Decisions

The main decisions still to be finalized are the managed switch, OPNsense hardware and network interfaces, and Wi-Fi 7 access point.

I'm also considering a second Proxmox node with 10Gb networking to make planned maintenance and VM recovery easier. Storage and migration options will need to be evaluated before choosing the hardware.

Reliability and recovery are important considerations, especially if the network and virtualized infrastructure depend on one another.

## Next Steps

- Finalize the firewall and switch hardware requirements.
- Determine the OPNsense WAN and LAN interface design.
- Define VLAN IDs, subnets, and DHCP scopes.
- Plan firewall rules between VLANs.
- Configure the Wi-Fi access point and map wireless networks to the appropriate VLANs.
- Evaluate a second Proxmox node and the storage and migration options.
- Test connectivity, isolation, and recovery before considering the overhaul complete.

I'll update this page as the design develops and document the final configuration once the network is implemented.
