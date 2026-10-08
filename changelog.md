# Infrastructure Change Log

This file records verified changes made to the infrastructure.

---

## 2026-10-07

### Repository and current-state documentation review
- Checked the live Proxmox host, VM inventory, PVE storage IDs, HomeServer reachability, and the enabled PBS backup timer.
- Confirmed the scheduled PBS workflow completed successfully on 2026-10-07, verified fresh backups for VMs 100, 101, 103, and 104, and shut the R440 down gracefully.
- Confirmed the repository backup runner and systemd unit files match the installed files on Host2. Added a repository overview and server, virtualization, and storage handovers; refreshed verified address and backup status details.
- This entry records a documentation audit; it does not describe a live configuration change.

---

## 2026-09-26

### Bathroom shower curtain automation
- Added a Home Assistant automation on `10.0.0.106` that closes both SwitchBot curtain entities when the bathroom humidity sensor crosses above 70% RH, waits 30 minutes, then opens both.
- Backed up `automations.yaml`; YAML validation passed with 18 automations. Restarted Home Assistant and verified the container is running and HTTP returns `200`. The physical curtain cycle was not triggered during verification.
- Restricted its trigger to 09:00–17:00 local Home Assistant time. Verified the YAML and that `automation.bathroom_shower_close_curtains` remains registered and enabled after restart.

### Aqara feeder mode check
- Restarted Home Assistant on `10.0.0.106` at the user's request to refresh the ZHA integration/device state for the Aqara feeder.
- Verified the container returned to `running` and HTTP returned `200`; `select.dry_food_feeder_mode` remained `unavailable`, so the internal schedule was not changed or verified. Existing `Dry Food` automation was left unchanged.
- Follow-up read-only diagnostics found the feeder checking in and reporting its manufacturer-specific schedule string, but ZHA's cached read of the feeding-mode attribute returned ZCL `UNSUPPORTED_ATTRIBUTE` (`0x86`); no feeder-specific Home Assistant log errors were present.
- User then sent a ZHA cluster attribute write for `feeding_mode=0` (`Manual`). ZHA recorded a successful mode value and a matching feeder attribute report, confirming Manual mode; the HA selector remains unavailable, and the stored schedule string remains on the device.
- Follow-up cache inspection showed the last feeding-source value was `0` at 09:00 America/Chicago, which the installed quirk renders as `undefined_0x00`. The source enum omits `0`; this value denotes an onboard-schedule feeding. The cached Manual-mode value `0` was reported at 09:30, after that feed. Thus the schedule did run for the last reported feed; the latest mode cache is Manual, but no later report confirms its current state and the schedule string remains stored. Updated the feeder handover to correct the earlier assumption that the write meant schedule use had been ruled out.
- Attempted to clear the onboard schedule through ZHA attribute `5011`, but the installed quirk rejects it with `KeyError: 5011`. The temporary startup automation used for the attempt was removed; the original 18 automations were restored. Restarted Home Assistant and verified HTTP `200`. The schedule was not cleared because this quirk does not expose the scheduling-string attribute.

### 2026-09-27 — Aqara feeder power cycle
- User physically power-cycled the feeder. ZHA saw it check in at 00:58 America/Chicago. Its latest cached last-feeding-source value is `2` (Remote/Home Assistant) from 00:02, but the feeding-mode cache has no post-power-cycle report. This does not yet prove the onboard schedule is disabled; verify against the next expected onboard feeding time.
- At 04:30:02, following the Home Assistant daily 04:30 feed automation, ZHA again reported last-feeding-source `2` (Remote/Home Assistant). The feeder checked in at 08:51. This supports that the 04:30 feed came from HA after the power cycle; the mode report remains stale and the stored schedule has not been cleared.

### Home Assistant cloud-control exceptions
- Recorded the user's local-control preference exceptions: existing WindmillAC cloud polling and TCL Home cloud control for the H25D44W dehumidifier.
- Installed TCL Home unofficial integration `3.16.0` on HomeServer `10.0.0.106`; backed up the Home Assistant config and verified the container is running with HTTP `200` and the integration module importable.
- Home Assistant registry inspection confirms a TCL Home config entry and dehumidifier entities, plus the ZHA humidity/water sensors and Pixel 9 mobile app. No TCL credentials are documented.

### Dehumidifier automations
- Added humidity control using the bathroom Zigbee sensor: turn on at `>=60%` RH, turn off at `<=55%` RH, and hold state in between. Baseline reading was `55.03%`; device's existing `50%` target was left as-is.
- Added a wet-water-sensor interlock that turns the dehumidifier off and notifies the Pixel 9 mobile app. Unknown/unavailable humidity also fails safe to off.
- Backed up the prior automation file to `/home/nick/automations.yaml-before-tcl-control-20260926-185051.bak` with mode `600`; Home Assistant restarted and both new automation entities were enabled. HTTP check returned `200`. Push delivery and wet-state shutdown were not actively triggered during verification.
- The configuration check surfaced four existing button automations referencing a missing ZHA config entry; they were left unchanged.

### Address changes — 2026-09-26 report, verified 2026-09-27
- Proxmox host `Host2` is at `10.0.0.99`; PBS server `backup` is at `10.0.0.100`; its iDRAC named `PBS` is at `10.0.0.101`.
- Verified PVE `9.2.20`, PBS `4.2.6`, PBS datastore connectivity, and Home Assistant reachability. The R440 hardware RAID 10 detail was confirmed by the user. See `networking.md` and `backup.md` for current details.

### PBS weekly backup workflow preparation
- Confirmed backup scope VMs `100`, `101`, `103`, and `104`; VM 104's 2026-09-27 PBS snapshot is visible from PVE. Planned schedule is Wednesday and Sunday at 02:00 America/Chicago.
- Verified iDRAC `PBS` at `10.0.0.101`, firmware `7.00.00.183` (user-reported), and its confirmed TLS certificate fingerprint. Redfish 1.17 service root responds with TLS validation.
- Installed `/usr/local/sbin/register-pbs-idrac-credential` on Host2, root-owned mode `0700`, to prompt locally without echo and store the credential using the TPM2-plus-host-key systemd mode. Corrected a temporary output-name mismatch after dummy-value verification. User provisioned the credential locally; authenticated, fingerprint-pinned inventory succeeded on 2026-09-28. iDRAC reports the server On and advertises `GracefulShutdown`; no power action was sent. No password was captured or documented.
- HomeServer `10.0.0.106` was reachable through Remote Desktop Commander; Home Assistant was running and `notify.mobile_app_pixel_9` was present. Added a local-only webhook automation and stored its random ID in `/config/secrets.yaml`, changing that file to mode `0600`. The initial Remote Desktop Commander outage interrupted webhook credential transfer; the transfer was then completed through the approved SSH path using RSA ciphertext and systemd TPM-plus-host encryption. No secret was printed or placed in a command argument.
- Initial runner and systemd files were staged in the workspace. They were subsequently deployed and validated as recorded below.

### PBS weekly backup workflow deployment and manual validation
- Installed `/usr/local/sbin/pbs-weekly-backup` and systemd units `pbs-weekly-backup.service`, `pbs-weekly-backup.timer`, and `pbs-weekly-backup-manual.service` on Host2. Enabled the Wednesday/Sunday 02:00 America/Chicago timer; systemd confirmed the next run as Wednesday 2026-09-30 02:00 CDT.
- Added Redfish TLS fingerprint pinning, TPM-plus-host encrypted iDRAC and HA webhook credentials, a host-wide lock, active vzdump conflict detection, PBS network/API/datastore readiness polling, 30-minute readiness, 12-hour task, and 15-minute graceful shutdown deadlines. Errors are logged to journald and sent to the Pixel 9 webhook when HA is available.
- Manual service backed up VMs 100, 101, 103, and 104. The PVE task finished `OK`, new PBS snapshots were verified for all four, and graceful shutdown completed. The R440 was already on at the beginning; this explicit manual service is allowed to shut it down after a fresh successful run. iDRAC confirmed the final state Off. No reboot was performed.
- A normal service test from PBS Off verified the full power-on/readiness/backup/shutdown path. iDRAC temporarily returned HTTP 503 while restarting after power-on; the runner was changed to retry transient Redfish unavailability until its 30-minute readiness deadline. PBS then became ready, all four backups and fresh snapshots succeeded, and iDRAC confirmed Off after graceful shutdown.
- Test failures first revealed `ProtectSystem=strict` blocking PVE task logs, then `PrivateTmp` hiding temporary QEMU config. The service sandbox was adjusted to `ProtectSystem=full`, writable `/etc/pve`, and no private temp directory. Final manual and normal runs succeeded.
- HA webhook test and workflow POSTs returned HTTP 200; HTTP 200 alone does not prove automation execution or phone delivery. HA port 8123 is HTTP, so its random webhook ID travels in the request path over the local LAN; no new firewall port was opened.
- 2026-09-27 21:13 CDT: Ran the normal workflow end to end from PBS Off. iDRAC powered on the R440; network, PBS API authentication, and datastore readiness passed; VMs 100, 101, 103, and 104 backed up; PVE task ended `OK`; fresh snapshots were verified; graceful shutdown completed; iDRAC confirmed `Off`. Host2's systemd service exited successfully. No configuration was changed.
- 2026-09-28: User reported the Pixel had not received a notification. Home Assistant's container start time preceded the final edits to `/config/automations.yaml` and `secrets.yaml`, and Recorder had no PBS automation entity; the automation had not loaded. Restarted only the Home Assistant container. Verified `automation.pbs_backup_result_notification` became `on`, sent one controlled webhook test, and the user confirmed the Pixel received it. PBS was not powered on or modified during this investigation.

### DEV VM
- Created Debian 13 VM.
- Configured static IP: `10.0.0.110/24`
- Gateway: `10.0.0.1`
- DNS: `10.0.0.107`
- Configured passwordless sudo for user `why`.
- Installed Node.js and npm.
- Installed OpenAI Codex CLI.

## 2026-09-27

### Curtain schedules and evening scene
- Added HA opening schedules for both curtains: Monday–Thursday at 07:15 and Friday at 07:45.
- Set each Curtain 3's SwitchBot integration movement speed to `1` (slow); the integration sends that speed for every open and close command.
- Created `scene.evening_curtains_and_lights` to close both curtains and turn on the dining room, bedroom, and living room lights. Changed the existing daily 17:00 `Lights on, 5pm` automation to call this scene.
- Backed up automations, scene configuration, and config-entry storage before editing. HA restarted, the config check completed with only the four known ZHA trigger errors, and the scene and automations registered. Physical operation was not tested. Native SwitchBot app schedules were not inspected or disabled.
- Changed the 05:00–09:00 bedside short-press sleep-reset automation from curtain toggle to explicit open, so pressing it while the curtains are already open cannot close them. Preserved the sleep-device reset actions and backed up the automation file. HA restarted, HTTP returned `200`, and the updated action was read back. The config check still reports the pre-existing missing ZHA entry for this button trigger; button operation was not physically tested.
- Raised the dehumidifier humidity-control start threshold from 60% to 65% RH; the stop threshold remains 55% RH. Backed up `automations.yaml`, restarted Home Assistant, and verified the updated templates, running container, and HTTP `200`. The config check continues to report the four previously documented missing ZHA trigger entries.

## 2026-09-28

### Dehumidifier humidity control
- Raised the start threshold from 65% to 70% RH on Home Assistant `10.0.0.106`; the stop threshold remained 55% RH and the water sensor interlock was unchanged. Backed up `/config/automations.yaml`, restarted Home Assistant, and verified the YAML parsed with 18 automations and the live template started at `>=70`. The physical dehumidifier response was not exercised.
- Raised the stop threshold from 55% to 57.5% RH; the start threshold remains 70% RH. Backed up `/config/automations.yaml`, restarted Home Assistant, and verified the YAML parsed with 18 automations and the live stop template is `<=57.5`. Physical operation was not exercised.

### Windmill AC schedule
- Updated the daily 20:00 `AC on` automation on Home Assistant `10.0.0.106` to check bedroom temperature from `sensor.meter_pro_co2_297b_temperature` above 66°F instead of the AC climate entity's `current_temperature`. Backed up `/config/automations.yaml`, restarted Home Assistant, and verified the YAML parses with 18 automations and the sensor condition. The schedule was not behaviorally exercised.
- Updated `automation.bathroom_shower_close_curtains` on `10.0.0.106` to turn on `light.bedroom_lights` after closing the curtains, then turn the light off after 30 minutes immediately before reopening them. Backed up `automations.yaml`, parsed and checked the configuration, restarted Home Assistant, and verified the container is running with HTTP `200`. The physical curtain/light cycle was not triggered during verification.
- Fixed HTTP 500 errors when opening automations in the HA GUI on `10.0.0.106`. The `PBS backup result notification` automation used `!secret` in GUI-managed `/config/automations.yaml`; HA's config-view parser rejected secrets in that file. Moved that automation to `/config/packages/pbs_backup_notifications.yaml`, included it through `homeassistant.packages`, and kept the webhook ID in `secrets.yaml`. Backed up the original automation and configuration files. Home Assistant's configuration check passed with only the four known missing-ZHA trigger errors; restarted the container and verified `running` plus HTTP `200`. The user confirmed the GUI automation view now works. See the Home Assistant handover for implementation details.

## 2026-10-02

- Changed the Windmill AC overnight shutoff on Home Assistant host `10.0.0.106` from 65°F/8 PM–8 AM to 68°F/8 PM–6 AM. The numeric threshold is `below: 68.1` to switch off at 68°F; retained the sensor-crossing and 20:00 time triggers and the existing automation ID. The former 08:00 was the end of the overnight interval after midnight. Backed up `/config/automations.yaml`, checked configuration (only four pre-existing ZHA trigger warnings), restarted Home Assistant, and verified HTTP `200` and the live rule. Temperature/time behavior was not exercised. See `homeassistant-docker-handoff.md`.
- Moved the overnight shutoff's clock trigger from 20:00 to 20:05 on `10.0.0.106`, leaving the 68°F cutoff, 8 PM–6 AM window, sensor-crossing trigger, and automation ID unchanged. The five-minute delay lets the daily 20:00 AC-on automation run first. Backed up `/config/automations.yaml`, checked configuration (only the four pre-existing ZHA trigger warnings), restarted Home Assistant, and verified HTTP `200` and the live trigger. See `homeassistant-docker-handoff.md`.
- Changed the overnight shutoff to check every minute from 20:05 to 06:00, in addition to the sensor-crossing trigger, so an already-below-threshold temperature is not missed. It only sends the off command while the AC state is `cool`. Configuration check showed only the four existing ZHA warnings; restarted Home Assistant, verified HTTP `200`, and observed the 23:26 CDT minute check turn the AC off with the sensor at 67.82°F. See `homeassistant-docker-handoff.md`.
- Lowered the Windmill AC overnight shutoff threshold from 68°F to 67°F on `10.0.0.106` (`below: 67.1` in the numeric-state trigger and condition). The 20:05–06:00 window, minute polling, and `cool` state guard are unchanged. Configuration check reported only the four existing ZHA warnings; restarted Home Assistant and verified HTTP `200` and that the AC remained off. The new threshold was not behaviorally exercised. See `homeassistant-docker-handoff.md`.
- Created scene ID `lights_off_except_bedroom_tv` on Home Assistant host `HomeServer` (`10.0.0.106`); its current display name is `TV Time`. After the user reported that running it turned off the TV lights, removed the aggregate `light.living_room_lights` target and retained individual living-room light targets. Bedroom Lights and TV Lights are excluded. The aggregate's membership has not been independently verified. Backed up `/config/scenes.yaml`, checked configuration (only four pre-existing ZHA trigger warnings), restarted Home Assistant, and verified HTTP `200`. The corrected scene was not activated during verification. See `homeassistant-docker-handoff.md`.
- Created `TV Reset` (`id: tv_reset`) as the inverse of `TV Time`: it turns on the same ten individual light targets and leaves Bedroom Lights and TV Lights unchanged. It omits the aggregate `light.living_room_lights` group. Backed up `/config/scenes.yaml`, checked configuration with only the four pre-existing ZHA warnings, restarted Home Assistant, and verified HTTP `200`. Physical behavior was not exercised. See `homeassistant-docker-handoff.md`.
- Removed `light.mya_s_bedroom_lamp_outlet` and `light.nick_s_bedroom_lamp_outlet` from both `TV Time` and `TV Reset` so both bedroom lamps are left alone, along with `light.bedroom_lights` and `light.h6056`. Each scene now targets eight lights. Backed up `/config/scenes.yaml`, checked configuration with only the four pre-existing ZHA warnings, restarted Home Assistant, and verified HTTP `200`. Physical behavior was not exercised. See `homeassistant-docker-handoff.md`.
