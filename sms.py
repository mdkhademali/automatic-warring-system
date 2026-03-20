"""
LMEWS — SMS Alert Module
Supports Twilio (real) and simulation mode (no API key needed)

Usage:
    from sms import send_sms, send_bulk_sms

Environment variables (optional — falls back to simulation):
    TWILIO_ACCOUNT_SID
    TWILIO_AUTH_TOKEN
    TWILIO_FROM_NUMBER
"""

import os
import json
import datetime
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# ── Configuration ─────────────────────────────────────────────────────
TWILIO_ACCOUNT_SID  = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN   = os.environ.get('TWILIO_AUTH_TOKEN')
TWILIO_FROM_NUMBER  = os.environ.get('TWILIO_FROM_NUMBER', '+1234567890')
SIMULATE            = not (TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN)

# Try to import Twilio (optional dependency)
try:
    from twilio.rest import Client as TwilioClient
    twilio_client = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN) if not SIMULATE else None
    TWILIO_AVAILABLE = True
except ImportError:
    twilio_client = None
    TWILIO_AVAILABLE = False
    logger.warning("Twilio library not installed — running in simulation mode")

# ── In-memory SMS log (replace with DB in production) ─────────────────
_sms_log: list[dict] = []

# ── Alert message templates (Bangla) ─────────────────────────────────
ALERT_MESSAGES = {
    "flood": {
        "bn": "সতর্কতা: নাটোরে বন্যার সম্ভাবনা। দ্রুত নিরাপদ স্থানে যান। —LMEWS",
        "en": "WARNING: Flood risk in Natore. Move to safe location immediately. —LMEWS"
    },
    "drought": {
        "bn": "সতর্কতা: খরার লক্ষণ দেখা যাচ্ছে। পানি সংরক্ষণ করুন। —LMEWS",
        "en": "ADVISORY: Drought conditions detected. Conserve water. —LMEWS"
    },
    "rain": {
        "bn": "সতর্কতা: আগামী ৬ ঘণ্টায় ভারী বৃষ্টির সম্ভাবনা। সাবধান থাকুন। —LMEWS",
        "en": "WARNING: Heavy rainfall expected in 6 hours. Stay safe. —LMEWS"
    },
    "lightning": {
        "bn": "সতর্কতা: বজ্রপাতের ঝুঁকি! খোলা মাঠে যাবেন না। ঘরের ভেতরে থাকুন। —LMEWS",
        "en": "WARNING: Lightning risk! Avoid open fields. Stay indoors. —LMEWS"
    },
    "earthquake": {
        "bn": "সতর্কতা: ভূমিকম্পের আশঙ্কা। খোলা জায়গায় আশ্রয় নিন। —LMEWS",
        "en": "WARNING: Earthquake alert. Move to open areas away from buildings. —LMEWS"
    },
}


def send_sms(
    to: str,
    message: str,
    simulate: bool = False,
    alert_type: Optional[str] = None,
) -> dict:
    """
    Send a single SMS. Falls back to simulation if Twilio is not configured.

    Args:
        to:          Recipient phone number (E.164 format, e.g. +8801711234567)
        message:     Message text (Bangla or English)
        simulate:    Force simulation mode
        alert_type:  Type tag for logging

    Returns:
        dict with status, sid, timestamp
    """
    ts = datetime.datetime.utcnow().isoformat() + "Z"
    log_entry = {
        "id":         len(_sms_log) + 1,
        "to":         to,
        "message":    message,
        "type":       alert_type or "manual",
        "timestamp":  ts,
        "status":     None,
        "sid":        None,
        "simulated":  None,
    }

    if SIMULATE or simulate or not TWILIO_AVAILABLE:
        # ── Simulation mode ──
        log_entry["status"]    = "delivered"
        log_entry["sid"]       = f"SIM-{len(_sms_log):06d}"
        log_entry["simulated"] = True
        _sms_log.append(log_entry)
        logger.info(f"[SIM] SMS → {to}: {message[:60]}…")
        return {"status": "delivered", "sid": log_entry["sid"], "simulated": True, "timestamp": ts}

    else:
        # ── Real Twilio send ──
        try:
            msg = twilio_client.messages.create(
                body=message,
                from_=TWILIO_FROM_NUMBER,
                to=to
            )
            log_entry["status"]    = "sent"
            log_entry["sid"]       = msg.sid
            log_entry["simulated"] = False
            _sms_log.append(log_entry)
            logger.info(f"[TWILIO] SMS sent → {to} | SID: {msg.sid}")
            return {"status": "sent", "sid": msg.sid, "simulated": False, "timestamp": ts}

        except Exception as e:
            log_entry["status"]    = "failed"
            log_entry["error"]     = str(e)
            log_entry["simulated"] = False
            _sms_log.append(log_entry)
            logger.error(f"[TWILIO] Failed → {to}: {e}")
            return {"status": "failed", "error": str(e), "timestamp": ts}


def send_bulk_sms(
    numbers: list[str],
    alert_type: str,
    lang: str = "bn",
    custom_message: Optional[str] = None,
) -> dict:
    """
    Send bulk SMS for a given alert type to a list of numbers.

    Args:
        numbers:        List of phone numbers
        alert_type:     One of flood/drought/rain/lightning/earthquake
        lang:           'bn' for Bangla, 'en' for English
        custom_message: Override default message

    Returns:
        Summary dict with sent/failed counts
    """
    message = custom_message or ALERT_MESSAGES.get(alert_type, {}).get(lang, "সতর্কতা! —LMEWS")
    results = {"sent": 0, "failed": 0, "total": len(numbers), "sids": []}

    for number in numbers:
        result = send_sms(number, message, alert_type=alert_type)
        if result["status"] in ("sent", "delivered"):
            results["sent"]  += 1
            results["sids"].append(result.get("sid"))
        else:
            results["failed"] += 1

    logger.info(f"Bulk SMS complete: {results['sent']}/{results['total']} sent for {alert_type}")
    return results


def get_sms_log(limit: int = 50) -> list[dict]:
    """Return the most recent SMS log entries."""
    return list(reversed(_sms_log))[:limit]


def get_sms_stats() -> dict:
    """Return aggregate SMS delivery statistics."""
    total     = len(_sms_log)
    delivered = sum(1 for e in _sms_log if e["status"] in ("sent", "delivered"))
    failed    = total - delivered
    return {
        "total":      total,
        "delivered":  delivered,
        "failed":     failed,
        "reach_rate": round(delivered / total * 100, 1) if total else 0,
        "simulated":  SIMULATE,
    }
