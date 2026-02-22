#!/usr/bin/env python3
"""Admin tool: create license records in license_server.sqlite.

Usage examples:
  python admin_create_license.py trial --days 30
  python admin_create_license.py standard
  python admin_create_license.py pro
  python admin_create_license.py unlimited

Env:
  LICENSE_DB (default: license_server.sqlite)
"""

import os
import secrets
import sqlite3
from datetime import datetime, timedelta, timezone

DB_PATH = os.environ.get("LICENSE_DB", "license_server.sqlite").strip()


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _db() -> sqlite3.Connection:
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def _init_db(con: sqlite3.Connection) -> None:
    cur = con.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS licenses (
          license_key TEXT PRIMARY KEY,
          tier TEXT NOT NULL,
          telegram_allowed INTEGER NOT NULL,
          updates_allowed INTEGER NOT NULL,
          issued_at TEXT NOT NULL,
          expires_at TEXT,
          max_devices INTEGER NOT NULL DEFAULT 1
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS activations (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          license_key TEXT NOT NULL,
          device_fingerprint TEXT NOT NULL,
          activated_at TEXT NOT NULL,
          UNIQUE(license_key, device_fingerprint)
        )
        """
    )
    con.commit()


def _gen_key() -> str:
    # Human-friendly: 4x5 chars
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    parts = []
    for _ in range(4):
        parts.append("".join(secrets.choice(alphabet) for _ in range(5)))
    return "-".join(parts)


def create_license(tier: str, *, days: int | None = None, max_devices: int = 1) -> str:
    tier = (tier or "").strip().lower()
    if tier not in ("trial", "standard", "pro", "unlimited"):
        raise SystemExit("tier must be: trial|standard|pro|unlimited")

    telegram_allowed = 1 if tier in ("pro", "unlimited") else 0
    updates_allowed = 1 if tier == "unlimited" else 0

    issued_at = _utc_now().isoformat()
    expires_at = None
    if tier == "trial":
        d = days or 30
        expires_at = (_utc_now() + timedelta(days=int(d))).isoformat()

    key = _gen_key()

    con = _db()
    _init_db(con)
    cur = con.cursor()
    cur.execute(
        """
        INSERT INTO licenses(license_key, tier, telegram_allowed, updates_allowed, issued_at, expires_at, max_devices)
        VALUES(?,?,?,?,?,?,?)
        """,
        (key, tier, telegram_allowed, updates_allowed, issued_at, expires_at, int(max_devices)),
    )
    con.commit()
    con.close()
    return key


def main() -> None:
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("tier", choices=["trial", "standard", "pro", "unlimited"])
    p.add_argument("--days", type=int, default=30, help="Only for trial")
    p.add_argument("--max-devices", type=int, default=1)
    args = p.parse_args()

    key = create_license(args.tier, days=args.days, max_devices=args.max_devices)
    print("LICENSE_KEY:", key)


if __name__ == "__main__":
    main()
