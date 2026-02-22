import base64
import json
import os
import platform
import subprocess
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
except Exception:  # pragma: no cover
    Ed25519PublicKey = None  # type: ignore


INSTANCE_DIR = Path(__file__).resolve().parent.parent / "instance"
LICENSE_KEY_PATH = INSTANCE_DIR / "license_key.txt"
ACTIVATION_PATH = INSTANCE_DIR / "license_activation.json"


@dataclass(frozen=True)
class LicenseStatus:
    ok: bool
    tier: str | None = None
    reason: str | None = None
    expires_at: str | None = None
    telegram_allowed: bool = False
    updates_allowed: bool = False


# Public key of activation server (Ed25519).
# Replace with your real public key (base64) when you deploy the license server.
LICENSE_SERVER_PUBLIC_KEY_B64 = os.environ.get("LICENSE_SERVER_PUBLIC_KEY_B64", "").strip()

APP_VERSION = (os.environ.get("APP_VERSION", "") or "").strip() or "kasir"


def _utc_now_ts() -> int:
    return int(datetime.now(timezone.utc).timestamp())


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8").strip()
    except Exception:
        return ""


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def get_license_key() -> str:
    key = (os.environ.get("KASIR_LICENSE_KEY", "") or "").strip()
    if key:
        return key
    return _read_text(LICENSE_KEY_PATH)


def save_license_key(key: str) -> None:
    _write_text(LICENSE_KEY_PATH, (key or "").strip())


def get_device_fingerprint() -> str:
    # Prefer explicit device fingerprint (best for Docker/local runs cross-OS)
    explicit = (os.environ.get("DEVICE_FINGERPRINT", "") or "").strip()
    if explicit:
        return explicit

    # Best-effort local fingerprint (not tamper-proof)
    parts: list[str] = [platform.system(), platform.release(), platform.machine(), platform.node()]

    # Windows: machine UUID (if available)
    if platform.system().lower() == "windows":
        try:
            out = subprocess.check_output(["wmic", "csproduct", "get", "uuid"], stderr=subprocess.DEVNULL)
            uuid = out.decode("utf-8", errors="ignore").splitlines()
            uuid = [x.strip() for x in uuid if x.strip() and "uuid" not in x.lower()]
            if uuid:
                parts.append(uuid[0])
        except Exception:
            pass

    # Linux/macOS: machine-id (if available)
    for p in ("/etc/machine-id", "/var/lib/dbus/machine-id"):
        try:
            if os.path.exists(p):
                parts.append(Path(p).read_text(encoding="utf-8").strip())
                break
        except Exception:
            pass

    raw = "|".join([x for x in parts if x])
    # Not cryptographic; just stable-ish
    return base64.urlsafe_b64encode(raw.encode("utf-8")).decode("ascii").rstrip("=")


def _load_activation() -> dict[str, Any] | None:
    try:
        data = json.loads(_read_text(ACTIVATION_PATH) or "{}")
        return data if isinstance(data, dict) else None
    except Exception:
        return None


def _save_activation(data: dict[str, Any]) -> None:
    ACTIVATION_PATH.parent.mkdir(parents=True, exist_ok=True)
    ACTIVATION_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _verify_activation_payload(payload_b64: str, sig_b64: str) -> dict[str, Any] | None:
    if not LICENSE_SERVER_PUBLIC_KEY_B64 or Ed25519PublicKey is None:
        return None

    try:
        pub_bytes = base64.b64decode(LICENSE_SERVER_PUBLIC_KEY_B64)
        pub = Ed25519PublicKey.from_public_bytes(pub_bytes)
        payload = base64.urlsafe_b64decode(payload_b64 + "==")
        sig = base64.urlsafe_b64decode(sig_b64 + "==")
        pub.verify(sig, payload)
        data = json.loads(payload.decode("utf-8"))
        return data if isinstance(data, dict) else None
    except Exception:
        return None


def validate_local_activation() -> LicenseStatus:
    act = _load_activation()
    if not act:
        return LicenseStatus(ok=False, reason="Activation token not found")

    payload_b64 = str(act.get("payload_b64") or "").strip()
    sig_b64 = str(act.get("sig_b64") or "").strip()
    data = _verify_activation_payload(payload_b64, sig_b64)
    if not data:
        return LicenseStatus(ok=False, reason="Activation token invalid (signature/key)")

    exp = int(data.get("exp") or 0)
    if exp and _utc_now_ts() > exp:
        return LicenseStatus(ok=False, reason="Activation token expired", expires_at=str(data.get("expires_at") or ""))

    tier = str(data.get("tier") or "").lower() or None
    telegram_allowed = bool(data.get("telegram_allowed") or False)
    updates_allowed = bool(data.get("updates_allowed") or False)
    return LicenseStatus(
        ok=True,
        tier=tier,
        expires_at=str(data.get("expires_at") or ""),
        telegram_allowed=telegram_allowed,
        updates_allowed=updates_allowed,
    )


def try_activate_online(timeout_s: int = 8) -> LicenseStatus:
    url = (os.environ.get("LICENSE_SERVER_URL", "") or "").strip()
    if not url:
        return LicenseStatus(ok=False, reason="LICENSE_SERVER_URL not set")

    key = get_license_key()
    if not key:
        return LicenseStatus(ok=False, reason="License key not set")

    device_fp = get_device_fingerprint()

    try:
        resp = requests.post(
            url.rstrip("/") + "/api/activate",
            json={
                "license_key": key,
                "device_fingerprint": device_fp,
                "app": "kasir",
                "app_version": APP_VERSION,
            },
            timeout=timeout_s,
        )
        if resp.status_code != 200:
            return LicenseStatus(ok=False, reason=f"Activation failed ({resp.status_code})")

        body = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {}
        if not isinstance(body, dict):
            return LicenseStatus(ok=False, reason="Activation response invalid")

        payload_b64 = str(body.get("payload_b64") or "").strip()
        sig_b64 = str(body.get("sig_b64") or "").strip()
        data = _verify_activation_payload(payload_b64, sig_b64)
        if not data:
            return LicenseStatus(ok=False, reason="Activation response signature invalid")

        _save_activation({"payload_b64": payload_b64, "sig_b64": sig_b64, "saved_at": int(time.time())})
        return validate_local_activation()
    except Exception as e:
        return LicenseStatus(ok=False, reason=f"Activation error: {e}")


def _should_ping(act: dict[str, Any] | None) -> bool:
    if (os.environ.get('LICENSE_PING', 'false') or 'false').lower() != 'true':
        return False
    if not act:
        return True
    last_ping = int(act.get('last_ping') or 0)
    # ping at most once per 6 hours
    return int(time.time()) - last_ping >= 6 * 3600


def try_ping_online(timeout_s: int = 4) -> None:
    url = (os.environ.get("LICENSE_SERVER_URL", "") or "").strip()
    if not url:
        return
    key = get_license_key()
    if not key:
        return
    device_fp = get_device_fingerprint()
    try:
        requests.post(
            url.rstrip('/') + '/api/ping',
            json={'license_key': key, 'device_fingerprint': device_fp, 'app_version': APP_VERSION},
            timeout=timeout_s,
        )
        act = _load_activation() or {}
        act['last_ping'] = int(time.time())
        _save_activation(act)
    except Exception:
        return


_cached_status: LicenseStatus | None = None


def get_license_status(refresh: bool = False) -> LicenseStatus:
    global _cached_status
    if _cached_status is not None and not refresh:
        return _cached_status

    status = validate_local_activation()
    if status.ok:
        act = _load_activation()
        if _should_ping(act):
            try_ping_online(timeout_s=3)
        _cached_status = status
        return status

    # If activation missing/expired, try online activation (best-effort)
    online = try_activate_online(timeout_s=6)
    _cached_status = online if online.ok else status
    return _cached_status


def allows_telegram() -> bool:
    st = get_license_status()
    return bool(st.ok and st.telegram_allowed)
