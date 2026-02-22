import base64
import json
import os
import secrets
import sqlite3
from datetime import datetime, timedelta, timezone

from flask import Flask, jsonify, request, render_template, redirect, session

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


DB_PATH = os.environ.get("LICENSE_DB", "license_server.sqlite").strip()
SIGNING_KEY_B64 = os.environ.get("LICENSE_SIGNING_KEY_B64", "").strip()
TOKEN_TTL_DAYS = int(os.environ.get("TOKEN_TTL_DAYS", "7"))

ADMIN_USER = (os.environ.get("ADMIN_USER", "") or "").strip()
ADMIN_PASS = (os.environ.get("ADMIN_PASS", "") or "").strip()
FLASK_SECRET_KEY = (os.environ.get("FLASK_SECRET_KEY", "") or "").strip() or secrets.token_hex(32)

app = Flask(__name__)
app.secret_key = FLASK_SECRET_KEY


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _db() -> sqlite3.Connection:
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def init_db() -> None:
    con = _db()
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

    # Lightweight migrations
    try:
        cols = {r[1] for r in cur.execute("PRAGMA table_info(activations)").fetchall()}
        if "last_seen" not in cols:
            cur.execute("ALTER TABLE activations ADD COLUMN last_seen TEXT")
        if "last_ip" not in cols:
            cur.execute("ALTER TABLE activations ADD COLUMN last_ip TEXT")
        if "last_app_version" not in cols:
            cur.execute("ALTER TABLE activations ADD COLUMN last_app_version TEXT")
    except Exception:
        pass

    con.commit()
    con.close()


def _get_private_key() -> Ed25519PrivateKey:
    if not SIGNING_KEY_B64:
        raise RuntimeError("LICENSE_SIGNING_KEY_B64 not set")
    key_bytes = base64.b64decode(SIGNING_KEY_B64)
    return Ed25519PrivateKey.from_private_bytes(key_bytes)


def _sign_payload(payload: dict) -> dict:
    priv = _get_private_key()
    payload_json = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    sig = priv.sign(payload_json)
    return {
        "payload_b64": base64.urlsafe_b64encode(payload_json).decode("ascii").rstrip("="),
        "sig_b64": base64.urlsafe_b64encode(sig).decode("ascii").rstrip("="),
    }


@app.post("/api/activate")
def activate():
    init_db()

    body = request.get_json(silent=True) or {}
    license_key = str(body.get("license_key") or "").strip()
    device_fp = str(body.get("device_fingerprint") or "").strip()

    if not license_key or not device_fp:
        return jsonify({"ok": False, "error": "license_key and device_fingerprint required"}), 400

    con = _db()
    cur = con.cursor()

    lic = cur.execute(
        "SELECT * FROM licenses WHERE license_key = ?",
        (license_key,),
    ).fetchone()

    if not lic:
        con.close()
        return jsonify({"ok": False, "error": "invalid license"}), 403

    expires_at = lic["expires_at"]
    if expires_at:
        try:
            exp_dt = datetime.fromisoformat(expires_at)
            if exp_dt.tzinfo is None:
                exp_dt = exp_dt.replace(tzinfo=timezone.utc)
            if _utc_now() > exp_dt:
                con.close()
                return jsonify({"ok": False, "error": "license expired"}), 403
        except Exception:
            con.close()
            return jsonify({"ok": False, "error": "license expires_at invalid"}), 500

    max_devices = int(lic["max_devices"] or 1)
    existing_devices = cur.execute(
        "SELECT device_fingerprint FROM activations WHERE license_key = ?",
        (license_key,),
    ).fetchall()
    device_set = {row[0] for row in existing_devices}

    if device_fp not in device_set and len(device_set) >= max_devices:
        con.close()
        return jsonify({"ok": False, "error": "device limit reached"}), 403

    cur.execute(
        "INSERT OR IGNORE INTO activations(license_key, device_fingerprint, activated_at) VALUES(?,?,?)",
        (license_key, device_fp, _utc_now().isoformat()),
    )

    # Update last_seen on activation
    cur.execute(
        """
        UPDATE activations
        SET last_seen = ?, last_ip = ?, last_app_version = ?
        WHERE license_key = ? AND device_fingerprint = ?
        """,
        (
            _utc_now().isoformat(),
            request.headers.get("X-Forwarded-For") or request.remote_addr,
            str(body.get("app_version") or "").strip() or None,
            license_key,
            device_fp,
        ),
    )
    con.commit()

    tier = str(lic["tier"] or "").lower()
    telegram_allowed = bool(int(lic["telegram_allowed"] or 0))
    updates_allowed = bool(int(lic["updates_allowed"] or 0))

    now = _utc_now()
    token_exp = now + timedelta(days=TOKEN_TTL_DAYS)

    payload = {
        "license_key": license_key,
        "tier": tier,
        "telegram_allowed": telegram_allowed,
        "updates_allowed": updates_allowed,
        "device_fingerprint": device_fp,
        "issued_at": lic["issued_at"],
        "expires_at": expires_at,
        "iat": int(now.timestamp()),
        "exp": int(token_exp.timestamp()),
    }

    signed = _sign_payload(payload)
    con.close()
    return jsonify(signed)


@app.post("/api/ping")
def ping():
    init_db()
    body = request.get_json(silent=True) or {}
    license_key = str(body.get("license_key") or "").strip()
    device_fp = str(body.get("device_fingerprint") or "").strip()
    app_version = str(body.get("app_version") or "").strip() or None

    if not license_key or not device_fp:
        return jsonify({"ok": False, "error": "license_key and device_fingerprint required"}), 400

    con = _db()
    cur = con.cursor()
    exists = cur.execute(
        "SELECT 1 FROM activations WHERE license_key = ? AND device_fingerprint = ?",
        (license_key, device_fp),
    ).fetchone()
    if not exists:
        con.close()
        return jsonify({"ok": False, "error": "not activated"}), 403

    cur.execute(
        """
        UPDATE activations
        SET last_seen = ?, last_ip = ?, last_app_version = ?
        WHERE license_key = ? AND device_fingerprint = ?
        """ ,
        (
            _utc_now().isoformat(),
            request.headers.get("X-Forwarded-For") or request.remote_addr,
            app_version,
            license_key,
            device_fp,
        ),
    )
    con.commit()
    con.close()
    return jsonify({"ok": True})


@app.get("/health")
def health():
    return jsonify({"ok": True})


def _admin_logged_in() -> bool:
    return bool(session.get("admin_ok"))


@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    if _admin_logged_in():
        return redirect("/admin/dashboard")

    error = None
    if request.method == "POST":
        u = (request.form.get("username") or "").strip()
        p = (request.form.get("password") or "").strip()
        if not ADMIN_USER or not ADMIN_PASS:
            error = "ADMIN_USER/ADMIN_PASS belum diset di server"
        elif u == ADMIN_USER and p == ADMIN_PASS:
            session["admin_ok"] = True
            return redirect("/admin/dashboard")
        else:
            error = "Login gagal"

    return render_template("admin/login.html", error=error)


@app.get("/admin/logout")
def admin_logout():
    session.clear()
    return redirect("/admin")


@app.get("/admin/dashboard")
def admin_dashboard():
    if not _admin_logged_in():
        return redirect("/admin")

    init_db()
    con = _db()
    cur = con.cursor()

    total_licenses = cur.execute("SELECT COUNT(*) FROM licenses").fetchone()[0]
    total_devices = cur.execute("SELECT COUNT(*) FROM activations").fetchone()[0]

    # active windows
    now = _utc_now()
    ts_24h = (now - timedelta(hours=24)).isoformat()
    ts_7d = (now - timedelta(days=7)).isoformat()
    active_24h = cur.execute("SELECT COUNT(*) FROM activations WHERE COALESCE(last_seen, activated_at) >= ?", (ts_24h,)).fetchone()[0]
    active_7d = cur.execute("SELECT COUNT(*) FROM activations WHERE COALESCE(last_seen, activated_at) >= ?", (ts_7d,)).fetchone()[0]

    tiers = cur.execute(
        """
        SELECT l.tier as tier,
               COUNT(DISTINCT l.license_key) as license_count,
               COUNT(a.device_fingerprint) as device_count
        FROM licenses l
        LEFT JOIN activations a ON a.license_key = l.license_key
        GROUP BY l.tier
        ORDER BY l.tier
        """
    ).fetchall()

    recent = cur.execute(
        """
        SELECT a.license_key, a.device_fingerprint, a.activated_at, a.last_seen, a.last_ip, a.last_app_version, l.tier
        FROM activations a
        JOIN licenses l ON l.license_key = a.license_key
        ORDER BY COALESCE(a.last_seen, a.activated_at) DESC
        LIMIT 50
        """
    ).fetchall()

    con.close()
    return render_template(
        "admin/dashboard.html",
        stats={
            "total_licenses": total_licenses,
            "total_devices": total_devices,
            "active_24h": active_24h,
            "active_7d": active_7d,
        },
        tiers=tiers,
        recent=recent,
    )


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8088")))
