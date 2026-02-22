#!/usr/bin/env python3
"""Standalone device fingerprint generator (no app dependency)."""

import base64
import os
import platform
from pathlib import Path


def get_device_fingerprint() -> str:
    explicit = (os.environ.get("DEVICE_FINGERPRINT", "") or "").strip()
    if explicit:
        return explicit

    parts = [platform.system(), platform.release(), platform.machine(), platform.node()]

    # macOS doesn't have /etc/machine-id by default; still try
    for p in ("/etc/machine-id", "/var/lib/dbus/machine-id"):
        try:
            if os.path.exists(p):
                parts.append(Path(p).read_text(encoding="utf-8").strip())
                break
        except Exception:
            pass

    raw = "|".join([x for x in parts if x])
    return base64.urlsafe_b64encode(raw.encode("utf-8")).decode("ascii").rstrip("=")


if __name__ == "__main__":
    print(get_device_fingerprint())
