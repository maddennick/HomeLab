#!/usr/bin/env python3
"""Fail-safe, single-run PBS orchestration for a configured PVE environment."""
import fcntl
import argparse
import hashlib
import http.client
import json
import logging
import os
import re
import ssl
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

# Configuration (set these in the service environment; the first six are required):
# PVE_NODE: PVE node name used for task and backup commands.
# PBS_STORAGE: PVE storage ID for the PBS datastore; PBS_HOST: address to ping while it starts.
# IDRAC_HOST: Redfish BMC address; IDRAC_CERT_SHA256: its verified 64-digit SHA-256 TLS fingerprint.
# PVE_GUEST_IDS: comma-separated guest IDs to back up. No production IDs are supplied here.
# The fingerprint may include colons. Obtain it through a trusted channel; it is checked before
# sending the credentials or power commands. Do not disable this check to work around a mismatch.
# CREDENTIALS_DIRECTORY: set by systemd; it must contain a JSON file with username and password.
# IDRAC_CREDENTIAL_NAME selects that file (default: "idrac"). Keep these credentials out of env vars
# and source control; provide them through systemd credentials instead.
# WEBHOOK_BASE_URL and WEBHOOK_CREDENTIAL_FILE are optional and must both be set to enable notices.
# The file is systemd-encrypted and contains only a webhook ID; the ID is appended to the base URL.
# PBS_BACKUP_LOCK_FILE optionally changes the local run lock path (default shown below).
NODE = os.environ.get("PVE_NODE", "<configure-pve-node>")
PBS_STORAGE = os.environ.get("PBS_STORAGE", "<configure-pbs-storage-id>")
PBS_HOST = os.environ.get("PBS_HOST", "<configure-pbs-host-or-ip>")
IDRAC_HOST = os.environ.get("IDRAC_HOST", "<configure-idrac-host-or-ip>")
IDRAC_FP = os.environ.get("IDRAC_CERT_SHA256", "<configure-idrac-sha256-fingerprint>").replace(":", "").upper()
GUESTS = tuple(x.strip() for x in os.environ.get("PVE_GUEST_IDS", "<configure-comma-separated-vm-ids>").split(",") if x.strip())
IDRAC_CREDENTIAL_NAME = os.environ.get("IDRAC_CREDENTIAL_NAME", "idrac")
CREDENTIALS_DIR = os.environ.get("CREDENTIALS_DIRECTORY")
WEBHOOK_CREDENTIAL_FILE = os.environ.get("WEBHOOK_CREDENTIAL_FILE", "")
WEBHOOK_BASE_URL = os.environ.get("WEBHOOK_BASE_URL", "")
LOCK_FILE = os.environ.get("PBS_BACKUP_LOCK_FILE", "/run/lock/pbs-weekly-backup.lock")
READY_SECONDS = 30 * 60
BACKUP_SECONDS = 12 * 60 * 60
SHUTDOWN_SECONDS = 15 * 60
POLL_SECONDS = 15

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("pbs-weekly-backup")


class WorkflowError(RuntimeError):
    pass


class RedfishUnavailable(WorkflowError):
    """Transient BMC restart or network outage while polling readiness."""


def validate_configuration():
    required = {
        "PVE_NODE": NODE, "PBS_STORAGE": PBS_STORAGE, "PBS_HOST": PBS_HOST,
        "IDRAC_HOST": IDRAC_HOST, "IDRAC_CERT_SHA256": IDRAC_FP,
        "PVE_GUEST_IDS": ",".join(GUESTS),
    }
    for name, value in required.items():
        if not value or value.startswith("<configure-"):
            raise WorkflowError(f"Set {name} to a value for this environment")
    if not re.fullmatch(r"[0-9A-F]{64}", IDRAC_FP):
        raise WorkflowError("IDRAC_CERT_SHA256 must be a 64-character SHA-256 fingerprint")
    if not GUESTS:
        raise WorkflowError("Set PVE_GUEST_IDS to at least one guest ID")


def run(argv, timeout=30):
    return subprocess.run(argv, capture_output=True, text=True, timeout=timeout)


def idrac_credentials():
    if not CREDENTIALS_DIR:
        raise WorkflowError("CREDENTIALS_DIRECTORY is not set; provide the BMC credential through systemd credentials")
    raw = Path(CREDENTIALS_DIR, IDRAC_CREDENTIAL_NAME).read_text()
    data = json.loads(raw)
    return data["username"], data["password"]


def redfish(path, method="GET", payload=None):
    user, password = idrac_credentials()
    token = __import__("base64").b64encode(f"{user}:{password}".encode()).decode()
    data = json.dumps(payload).encode() if payload is not None else None
    connection = http.client.HTTPSConnection(IDRAC_HOST, context=ssl._create_unverified_context(), timeout=10)
    try:
        connection.connect()
        cert = connection.sock.getpeercert(binary_form=True)
        fingerprint = hashlib.sha256(cert).hexdigest().upper()
        if fingerprint != IDRAC_FP:
            raise WorkflowError("BMC TLS certificate fingerprint changed")
        # Only send credentials or a power request after verifying the server certificate.
        headers = {"Authorization": f"Basic {token}", "Accept": "application/json",
                   "Content-Type": "application/json"}
        connection.request(method, path, body=data, headers=headers)
        response = connection.getresponse()
        if response.status in (500, 502, 503, 504):
            raise RedfishUnavailable(f"BMC temporarily returned HTTP {response.status}")
        if response.status not in (200, 202, 204):
            raise WorkflowError(f"BMC {method} {path} returned HTTP {response.status}")
        if method == "GET":
            return json.loads(response.read())
        return response.status
    except WorkflowError:
        raise
    except (OSError, TimeoutError, http.client.HTTPException) as exc:
        raise RedfishUnavailable(f"BMC {method} {path} unavailable ({type(exc).__name__})") from None
    except Exception as exc:
        raise WorkflowError(f"BMC {method} {path} failed ({type(exc).__name__})") from None
    finally:
        connection.close()


def pbs_storage_ready():
    try:
        ping = run(["ping", "-n", "-c", "1", "-W", "2", PBS_HOST], timeout=5)
    except subprocess.TimeoutExpired:
        return False, "PBS ping check timed out"
    if ping.returncode:
        return False, "PBS ping failed"
    # Ping alone can pass before PBS is usable; also require PVE's authenticated datastore query.
    try:
        result = run(["pvesm", "status", "--storage", PBS_STORAGE], timeout=20)
    except subprocess.TimeoutExpired:
        return False, "PBS authenticated datastore query timed out"
    if result.returncode:
        return False, "PVE could not authenticate to PBS or query storage"
    rows = [line.split() for line in result.stdout.splitlines()]
    if not any(len(row) > 2 and row[0] == PBS_STORAGE and row[2] == "active" for row in rows):
        return False, f"PBS datastore {PBS_STORAGE} is not active"
    return True, "PBS network, API authentication, and datastore are ready"


def active_vzdump_tasks():
    result = run(["pvesh", "get", f"/nodes/{NODE}/tasks", "--source", "active",
                  "--typefilter", "vzdump", "--limit", "100", "--output-format", "json"], timeout=30)
    if result.returncode:
        raise WorkflowError("Could not check for an already running vzdump task")
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        raise WorkflowError("PVE returned an unreadable active task list") from None


def recent_vzdump_tasks(since):
    result = run(["pvesh", "get", f"/nodes/{NODE}/tasks", "--source", "all",
                  "--typefilter", "vzdump", "--since", str(max(0, since - 5)),
                  "--limit", "100", "--output-format", "json"], timeout=30)
    if result.returncode:
        raise WorkflowError("Could not find the PVE task created by this run")
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        raise WorkflowError("PVE returned an unreadable recent task list") from None


def task_status(upid):
    result = run(["pvesh", "get", f"/nodes/{NODE}/tasks/{upid}/status", "--output-format", "json"], timeout=30)
    if result.returncode:
        raise WorkflowError("Could not read the PVE backup task status")
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        raise WorkflowError("PVE returned an unreadable backup task status") from None


def start_backup():
    started = int(time.time())
    deadline = time.monotonic() + BACKUP_SECONDS
    command = ["pvesh", "create", f"/nodes/{NODE}/vzdump", "--vmid", ",".join(GUESTS),
               "--storage", PBS_STORAGE, "--mode", "snapshot", "--compress", "zstd",
               "--notification-mode", "auto", "--output-format", "json"]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                               start_new_session=True)
    try:
        stdout, stderr = process.communicate(timeout=BACKUP_SECONDS)
    except subprocess.TimeoutExpired:
        process.terminate()
        try:
            process.communicate(timeout=30)
        except subprocess.TimeoutExpired:
            process.kill()
            process.communicate()
        running = active_vzdump_tasks()
        detail = "; active task(s): " + ", ".join(item.get("upid", "unknown") for item in running) if running else ""
        raise WorkflowError("PVE backup command exceeded the 12 hour deadline" + detail) from None
    if process.returncode:
        detail = (stderr or stdout).strip()
        detail = re.sub(r"(?i)(password|token|authorization)\s*[:=]\s*\S+", r"\1=<redacted>", detail)
        detail = detail[:400] or "no error detail returned"
        raise WorkflowError("PVE refused to start the required multi guest backup: " + detail)
    try:
        upid = json.loads(stdout)
    except json.JSONDecodeError:
        upid = stdout.strip().strip('"')
    if not isinstance(upid, str) or not upid.startswith("UPID:"):
        matches = [item for item in recent_vzdump_tasks(started)
                   if item.get("type") == "vzdump" and int(item.get("starttime", 0)) >= started - 2]
        if not matches:
            raise WorkflowError("PVE did not return or record a backup task ID")
        upid = max(matches, key=lambda item: int(item.get("starttime", 0))).get("upid")
    if not isinstance(upid, str) or not upid.startswith("UPID:"):
        raise WorkflowError("PVE returned a malformed backup task ID")
    log.info("Tracking PVE backup task %s", upid)
    while time.monotonic() < deadline:
        state = task_status(upid)
        if state.get("status") == "stopped":
            if state.get("exitstatus") != "OK":
                raise WorkflowError(f"PVE backup task ended with status {state.get('exitstatus', 'unknown')}")
            return started, upid
        time.sleep(POLL_SECONDS)
    raise WorkflowError(f"Backup task {upid} exceeded the 12 hour deadline; PBS will remain on")


def verify_snapshots(started):
    # Do not treat a successful task response as sufficient: require a fresh snapshot per guest.
    missing = []
    for vmid in GUESTS:
        result = run(["pvesm", "list", PBS_STORAGE, "--content", "backup", "--vmid", vmid], timeout=90)
        if result.returncode:
            raise WorkflowError(f"Could not verify PBS snapshots for guest {vmid}")
        fresh = False
        for match in re.finditer(r"vm/" + re.escape(vmid) + r"/(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ)", result.stdout):
            try:
                stamp = datetime.strptime(match.group(1), "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).timestamp()
                fresh |= stamp >= started - 2
            except ValueError:
                continue
        if not fresh:
            missing.append(vmid)
    if missing:
        raise WorkflowError("No new PBS snapshot was verified for guest(s): " + ", ".join(missing))


def notify(message, failed=False):
    """Send a best-effort push notice through an optional webhook."""
    # Both settings are required. The secret ID stays in an encrypted credential, not the URL/config.
    if not WEBHOOK_CREDENTIAL_FILE or not WEBHOOK_BASE_URL:
        log.info("Webhook notification is not configured; notification was not sent")
        return
    secret_file = Path(WEBHOOK_CREDENTIAL_FILE)
    if not secret_file.exists():
        log.warning("Webhook credential is unavailable; notification was not sent")
        return
    try:
        decrypted = run(["systemd-creds", "decrypt", str(secret_file), "-"], timeout=10)
    except Exception as exc:
        log.error("Could not decrypt the webhook credential (%s)", type(exc).__name__)
        return
    if decrypted.returncode:
        log.error("Could not decrypt the webhook credential")
        return
    webhook_id = decrypted.stdout.strip()
    if not webhook_id:
        log.warning("Webhook credential is empty; notification was not sent")
        return
    payload = json.dumps({"title": "PBS backup " + ("FAILED" if failed else "succeeded"),
                          "message": message}).encode()
    req = urllib.request.Request(WEBHOOK_BASE_URL.rstrip("/") + "/" + webhook_id,
                                 data=payload, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status not in (200, 202, 204):
                log.error("Webhook notification returned HTTP %s", response.status)
            else:
                log.info("Notification endpoint accepted the result (HTTP %s)", response.status)
    except Exception as exc:
        log.error("Webhook notification failed (%s); see journal for backup result", type(exc).__name__)


def main(shutdown_even_if_already_on=False):
    validate_configuration()
    # The non-blocking lock prevents overlapping scheduled/manual runs from racing power control.
    lock = open(LOCK_FILE, "w")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        raise WorkflowError("Another PBS backup workflow run already holds the lock") from None

    # Avoid interfering with a backup started outside this workflow.
    running = active_vzdump_tasks()
    if running:
        ids = ", ".join(str(item.get("upid", "unknown")) for item in running)
        raise WorkflowError("An existing vzdump task is still active: " + ids)

    system = redfish("/redfish/v1/Systems/System.Embedded.1")
    state = system.get("PowerState")
    if state not in ("On", "Off"):
        raise WorkflowError(f"Unexpected BMC power state: {state!r}")
    powered_here = state == "Off"
    if powered_here:
        try:
            redfish("/redfish/v1/Systems/System.Embedded.1/Actions/ComputerSystem.Reset",
                    "POST", {"ResetType": "On"})
            log.info("Sent BMC power-on request")
        except RedfishUnavailable as exc:
            log.warning("Power-on response was interrupted (%s); will verify through readiness polling", exc)
    else:
        if shutdown_even_if_already_on:
            log.info("BMC was already on; manual mode will shut it down only after verified backup success")
        else:
            log.info("BMC was already on; it will be left on after this run")

    # Proceed only when both the BMC reports the host on and PBS storage is authenticated and active.
    deadline = time.monotonic() + READY_SECONDS
    last_reason = "PBS is not ready yet"
    while time.monotonic() < deadline:
        try:
            current = redfish("/redfish/v1/Systems/System.Embedded.1")
        except RedfishUnavailable as exc:
            last_reason = str(exc)
            time.sleep(POLL_SECONDS)
            continue
        if current.get("PowerState") != "On":
            last_reason = "BMC host has not reached power state On"
        else:
            ready, last_reason = pbs_storage_ready()
            if ready:
                break
        time.sleep(POLL_SECONDS)
    else:
        raise WorkflowError("PBS did not become ready within 30 minutes: " + last_reason)

    log.info("%s", last_reason)
    started, upid = start_backup()
    verify_snapshots(started)
    log.info("All required backups succeeded and fresh snapshots were verified (task %s)", upid)

    # Shut down only after every fresh snapshot is verified, and only if this run powered the host
    # on (unless an operator explicitly requested the manual override).
    if powered_here or shutdown_even_if_already_on:
        try:
            redfish("/redfish/v1/Systems/System.Embedded.1/Actions/ComputerSystem.Reset",
                    "POST", {"ResetType": "GracefulShutdown"})
        except RedfishUnavailable as exc:
            log.warning("Graceful-shutdown response was interrupted (%s); checking BMC power state", exc)
        deadline = time.monotonic() + SHUTDOWN_SECONDS
        while time.monotonic() < deadline:
            try:
                current = redfish("/redfish/v1/Systems/System.Embedded.1")
            except RedfishUnavailable:
                time.sleep(POLL_SECONDS)
                continue
            if current.get("PowerState") == "Off":
                log.info("Host completed graceful shutdown")
                break
            time.sleep(POLL_SECONDS)
        else:
            raise WorkflowError("Graceful shutdown was requested but BMC still reports On after 15 minutes")
    notify(f"Guest backups {', '.join(GUESTS)} completed and PBS snapshots were verified.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the fail-safe PBS boot/backup workflow")
    parser.add_argument("--manual-shutdown-after-success", action="store_true",
                        help="manual-only override: gracefully shut down after this run verifies every fresh backup, even if PBS started on")
    args = parser.parse_args()
    try:
        main(shutdown_even_if_already_on=args.manual_shutdown_after_success)
    except Exception as exc:
        message = str(exc) or type(exc).__name__
        log.error("FAILED: %s; no shutdown request will be sent", message)
        try:
            notify(message, failed=True)
        except Exception as notify_exc:
            log.error("Failure notification also failed (%s)", type(notify_exc).__name__)
        sys.exit(1)
