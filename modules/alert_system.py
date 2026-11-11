"""
modules/alert_system.py - Emergency alert dispatcher with cooldown & DB tracking
"""
import time
import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import ALERT_COOLDOWN_S, EMAIL_RECEIVER
from utils.email_utils import send_alert_email
from database.db import mark_notified, save_notification

# In-memory cooldown: {source_name: last_alert_epoch}
_last_alert: dict = {}


def maybe_send_alert(
    accident_id: int,
    source_name: str,
    source_type: str,
    confidence: float,
    severity: str,
    snapshot_path: str = None,
    location: str = "Not configured",
):
    """
    Send an email alert ONLY IF:
      1. Email is configured.
      2. Cooldown period has elapsed for this source.
    Records result in DB; never claims success without actual send.
    """
    if not EMAIL_RECEIVER:
        return   # silently skip — user hasn't configured email

    now = time.time()
    last = _last_alert.get(source_name, 0)
    if now - last < ALERT_COOLDOWN_S:
        return   # cooldown active

    from datetime import datetime
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ok, msg = send_alert_email(
        accident_id=accident_id,
        source_name=source_name,
        source_type=source_type,
        timestamp=ts,
        confidence=confidence,
        severity=severity,
        snapshot_path=snapshot_path,
        location=location,
    )

    status = "sent" if ok else "failed"
    save_notification(accident_id, EMAIL_RECEIVER, status, None if ok else msg)

    if ok:
        mark_notified(accident_id)
        _last_alert[source_name] = now
    # Errors are logged to DB; we don't raise exceptions here.
