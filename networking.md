# Networking Handover

## Current known addressing

| System | Address | Notes |
|---|---|---|
| Proxmox host `Host2` | `10.0.0.99/24` | Verified on 2026-10-07. Gateway `10.0.0.1`; DNS `10.0.0.107`. |
| PBS host `backup` | `10.0.0.100` | Dell PowerEdge R440. Address and PBS service were reached by the successful scheduled workflow on 2026-10-07; host is powered off after that run. Mask, gateway, and DNS last verified 2026-09-27. |
| PBS iDRAC `PBS` | `10.0.0.101` | User-reported address; HTTPS/Redfish port 443. Authenticated power workflow succeeded on 2026-10-07. |
| HomeServer VM | `10.0.0.106` | Verified by SSH on 2026-10-07; VM and Home Assistant/Matter containers were running. |
| DEV VM | `10.0.0.110/24` | Previously recorded with gateway `10.0.0.1` and DNS `10.0.0.107`; current address not rechecked. |

## Change history

### 2026-09-26 — Host address migration (later verified)

- Proxmox host `Host2` is currently at `10.0.0.99`; the PBS host `backup` is at `10.0.0.100`. Both addresses and roles were verified on 2026-09-27.
- Immich handover SSH proxy examples now use the current Proxmox host address, `10.0.0.99`.

### 2026-09-27 — PBS iDRAC address

- User identified the R440 iDRAC as `PBS` at `10.0.0.101`. Host2 can reach it on HTTPS port 443.
- See `backup.md` for the verified certificate fingerprint and backup automation status.

### 2026-10-07 — Current-state check

- Rechecked Host2's address, gateway, and DNS on the live host.
- Verified HomeServer at `10.0.0.106` by SSH. The scheduled backup workflow also reached PBS at `10.0.0.100` and iDRAC at `10.0.0.101`; PBS is expected to be off after the successful run.
- DEV's recorded address was not rechecked and should be treated as needing verification.
