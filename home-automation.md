# Home Automation

Home Assistant and Matter Server run as Docker Compose services on the `HomeServer` Debian VM.

- Home Assistant provides integrations, device automation, and notifications.
- Matter Server provides a local WebSocket endpoint at `ws://localhost:5580/ws`.
- Configuration and Matter data persist on the VM.

On 2026-10-07, the Home Assistant container was running and its local HTTP endpoint returned `200`. Matter Server was running; a recent peer subscription timeout recovered through re-subscription. Device-level health was not checked.

See the [Home Assistant](../handover/homeassistant-docker-handoff.md) and [Matter Server](../handover/homeassistant-matter-server-handoff.md) handovers for basic operating notes.
