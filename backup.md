# PBS Backup Handover

## Current environment — reviewed 2026-10-07

- Proxmox VE host: `Host2`, `10.0.0.99`, PVE `9.2.20`.
- PBS host: Dell PowerEdge R440, hostname `backup`, `10.0.0.100`, PBS `4.2.6`.
- iDRAC name `PBS`, `10.0.0.101`, firmware `7.00.00.183` (reported by user).
- PBS datastore: `pbs-backup`, path `/backup`.
- User confirms the R440 uses a hardware RAID 10 controller. PBS sees an ext4 root filesystem on an LVM virtual block device; `/backup` is a directory on that filesystem. No ZFS pool is configured in PBS.
- PBS API and proxy services and datastore access were last directly audited on 2026-09-27. The scheduled workflow reached the PBS API and datastore successfully on 2026-10-07.
- PBS is currently expected to be powered off: the successful scheduled run on 2026-10-07 performed a graceful shutdown after verifying backups.

## Existing PVE/PBS configuration

- PVE storage ID `pbs-backup` points to server `10.0.0.100`, datastore `pbs-backup`.
- Current PVE storage account is `root@pam`; its secret is stored in PVE's private storage credential file. Do not read or document the secret. A least-privilege PBS account remains a recommended follow-up.
- PVE has no native scheduled backup job; the workflow below is scheduled by a systemd timer on Host2.
- PBS was configured with a daily prune job (keep 7 last, 7 daily, 4 weekly, 3 monthly, and 1 yearly) and daily garbage collection when last inspected on 2026-09-27. Recheck these maintenance schedules when PBS is powered on.
- Latest verified scheduled PVE task on 2026-10-07 ran as `UPID:Host2:0005C641:00AEFB65:6AC5EE9F:vzdump::root@pam:` and finished `OK`. The runner verified fresh PBS snapshots for VMs 100, 101, 103, and 104 before shutdown. The task and snapshot verification are recorded in Host2's journal.

## Enabled backup workflow

- User-confirmed scope: VMs `100`, `101`, `103`, and `104`; exclude stopped template VM `102` unless scope changes.
- Enabled systemd timer runs Wednesday and Sunday at 02:00 `America/Chicago`. On 2026-10-07, its last trigger was verified at 02:00:03 CDT and its next run was scheduled for Sunday 2026-10-11 at 02:00 CDT.
- Host2 runs PVE's native multi guest `vzdump` task to `pbs-backup`, polls the actual PVE task status, and verifies a fresh PBS snapshot for every required VM.
- iDRAC Redfish uses its confirmed SHA-256 certificate fingerprint and systemd TPM-plus-host encrypted credential. If the R440 is Off, the runner powers it on and waits for iDRAC On, ping, authenticated `pvesm status`, and active datastore. No fixed sleep is used as readiness proof.
- Scheduled and safe manual runs shut PBS down only if that run powered it on. If PBS started On, they leave it On. Failure paths never issue shutdown; if that run already powered PBS on, it remains on for troubleshooting.
- `pbs-weekly-backup-manual.service` is an explicit operator override that performs a fresh backup of every required guest and gracefully shuts PBS down after success even if it started On. It is not attached to the timer.
- Home Assistant local-only webhook sends success/failure messages to `notify.mobile_app_pixel_9`. On 2026-09-28, investigation found that Home Assistant last started before `automations.yaml` and `secrets.yaml` were edited, so the PBS automation had not loaded. Restarted only the Home Assistant container to load the current YAML; verified entity `automation.pbs_backup_result_notification` appeared `on`, then POSTed one controlled test. The user confirmed that the Pixel received it. The runner's HTTP 200 alone remains only webhook acceptance, not proof of phone delivery. The random webhook ID is in HA `secrets.yaml` mode `0600` and a systemd TPM-plus-host encrypted credential. HA serves HTTP, so the ID travels on the trusted LAN in the request path; keep the LAN trusted or add TLS protection to HA before extending this use.
- Deadlines: PBS readiness 30 minutes, backup task 12 hours, graceful shutdown 15 minutes. A host-wide `flock` and active-task query prevent overlap. Timeout/failure does not cause a shutdown.
- Installed on Host2: `/usr/local/sbin/pbs-weekly-backup`, `/etc/systemd/system/pbs-weekly-backup.service`, `/etc/systemd/system/pbs-weekly-backup.timer`, and `/etc/systemd/system/pbs-weekly-backup-manual.service`. Timer is enabled and active.
- Manual safe run: `systemctl start pbs-weekly-backup.service`. Manual boot/backup/verified-shutdown run: `systemctl start pbs-weekly-backup-manual.service`. Inspect with `journalctl -u pbs-weekly-backup.service` or `journalctl -u pbs-weekly-backup-manual.service`.
- Services use `ProtectSystem=full`, `ProtectHome=yes`, and `NoNewPrivileges=yes`; `/etc/pve` is writable because PVE needs temporary guest configuration updates for snapshots. `PrivateTmp` is omitted because QEMU cannot see PVE's temporary backup config through a private `/tmp`.
- The timer has `Persistent=false`; if Host2 is off at a scheduled time, systemd does not run a catch-up job at boot. The following Wednesday/Sunday schedule is the next attempt.
- On 2026-10-07, SHA-256 checksums of the workspace runner and all three systemd unit files matched the installed files on Host2. The enabled timer and its next scheduled run were also verified live.

## iDRAC identity and credentials

- Dell self-signed certificate SHA-256 fingerprint, confirmed by user on 2026-09-27: `47:9B:8F:E1:5D:08:3C:15:ED:F5:D5:D5:D8:49:23:8D:FB:59:C0:62:6E:F3:9A:38:D2:73:6F:94:47:2A:15:C4`.
- Host2 verified the fingerprint and retrieved the unauthenticated Redfish service root over TLS. Redfish reports version `1.17.0`; system inventory requires authentication.
- Dedicated iDRAC account username is `PBS`. Password is never to be documented or sent in chat.
- Credential enrollment helper installed on Host2: `/usr/local/sbin/register-pbs-idrac-credential`, root-owned mode `0700`. It reads the password from a local terminal without echo and writes a systemd credential bound to the Host2 TPM2 and host key at `/etc/credstore.encrypted/pbs-idrac`.
- On 2026-09-28, the encrypted credential was verified present with root-only permissions. A TLS-fingerprint-pinned, authenticated Redfish GET succeeded. The R440 reported power state `On`; the reset action advertises `On` and `GracefulShutdown` among its allowed values. That inventory check sent GET requests only.
- The dedicated iDRAC account is enabled with Dell's `Operator` role. This is less privileged than Administrator and permits power operations; no custom narrower role was confirmed by Redfish.
- Manual integration test on 2026-09-27: R440 was already On. All four VMs backed up, the PVE task ended `OK`, fresh snapshots were verified, graceful shutdown completed, and iDRAC confirmed `Off`. No reboot was done.
- Normal scheduled service test on 2026-09-27: iDRAC powered the R440 on, its temporary HTTP 503 during startup was retried, PBS became reachable and active, all four backups completed and snapshots were verified, and the runner shut down gracefully. iDRAC confirmed `Off`. Current expected state: PBS Off.
- Full manual workflow test on 2026-09-27 at 21:13 CDT: PBS was Off at start. The normal service powered it on, waited until network/API/datastore checks passed, backed up VMs `100`, `101`, `103`, and `104`, verified the PVE task ended `OK` and fresh snapshots existed, then shut down gracefully. iDRAC confirmed `Off`; the systemd service exited successfully. HA accepted the result webhook. No PBS or PVE configuration was changed.
- Failed test attempts exposed systemd sandbox incompatibilities (`/var/log/pve/tasks` read-only, private `/tmp` hiding QEMU config) and a transient iDRAC 503. These were corrected with `ProtectSystem=full`, writable `/etc/pve`, no `PrivateTmp`, and bounded Redfish retries after power-on. The final normal and manual runs succeeded.

## Change history

### 2026-10-07 — Scheduled run and deployment parity verified

- Inspected the live systemd journal after the scheduled 02:00 CDT run. iDRAC powered on the R440, PBS became reachable, and the PVE multi-guest backup completed successfully for VMs `100`, `101`, `103`, and `104`.
- The runner verified a fresh PBS snapshot for each required VM, then PBS completed a graceful shutdown. Home Assistant accepted the result webhook (HTTP 200); this confirms webhook acceptance, not independent phone delivery.
- Confirmed the timer is enabled and active, with its next run scheduled for 2026-10-11 at 02:00 CDT. The inactive PVE PBS storage after the run is expected while the PBS host is off.
- SHA-256 checksums for the runner and the scheduled, manual, and timer unit files matched the copies installed on Host2.

### 2026-09-27 — Audit and credential enrollment preparation

- Verified PVE/PBS versions, storage registration and access, guest inventory, current snapshots, PBS maintenance jobs, and iDRAC network/TLS identity.
- Added and syntax-checked the root-only credential enrollment helper on `Host2`; its TPM2-plus-host-key encrypt/decrypt path passed a dummy-value check. Corrected a temporary filename mismatch before enrollment. The user provisioned the dedicated credential locally; authenticated, certificate-pinned Redfish inventory succeeded on 2026-09-28, and the live power state was `On`. The account's advertised `GracefulShutdown` action was confirmed with GET-only inspection. No power action was sent.
- Confirmed the hardware RAID 10 detail with the user. PBS's filesystem remains ext4 on the RAID-backed virtual volume; `/backup` shares the root filesystem.

### 2026-09-27 — Backup workflow deployment and manual validation

- Added the HA local-only webhook automation and protected `/config/secrets.yaml` with mode `0600`. YAML parsed as 19 automations and the webhook returned HTTP 200 for a test push request. Physical phone delivery was not independently confirmed.
- Installed `/usr/local/sbin/pbs-weekly-backup` and the scheduled/manual systemd units. Python syntax, systemd unit validation, and calendar parsing passed. Enabled the Wednesday/Sunday timer; next run is Wednesday 2026-09-30 02:00 CDT.
- Manual run backed up VMs 100, 101, 103, and 104 successfully, verified a new PBS snapshot for each, and completed graceful shutdown. iDRAC GET confirmed the final power state Off.
- User can start a normal safe manual run with `systemctl start pbs-weekly-backup.service` or an explicit fresh-backup-and-shutdown run with `systemctl start pbs-weekly-backup-manual.service`. Logs are in the systemd journal.
