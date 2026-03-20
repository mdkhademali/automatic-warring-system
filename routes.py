"""
LMEWS — API Routes
All Flask API endpoints for alerts, SMS, environmental data, volunteers
"""

import json
import random
import datetime
from flask import Blueprint, jsonify, request
from sms import send_sms, send_bulk_sms, get_sms_log, get_sms_stats, ALERT_MESSAGES

# ── Sample registered numbers (real system: from DB) ─────────────────
REGISTERED_NUMBERS = [
    "+8801711234567", "+8801812345678", "+8801913456789",
    "+8801714567890", "+8801515678901", "+8801616789012",
    "+8801717890123", "+8801818901234", "+8801919012345",
]

# ── Upazila data ──────────────────────────────────────────────────────
UPAZILAS = ["Natore Sadar", "Baraigram", "Gurudaspur", "Lalpur", "Singra", "Atrai", "Naldanga"]


def register_routes(app):

    # ── Alert APIs ────────────────────────────────────────────────────

    @app.route('/api/alerts')
    def get_alerts():
        """Current risk levels for all hazard types."""
        return jsonify({
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "district":  "Natore",
            "alerts": [
                {
                    "type": "flood",
                    "level": "HIGH",
                    "color": "#ef4444",
                    "message_bn": ALERT_MESSAGES["flood"]["bn"],
                    "message_en": ALERT_MESSAGES["flood"]["en"],
                    "affected": ["Natore Sadar", "Baraigram"],
                    "actions": ["Move to elevated shelter", "Avoid rivers", "Call 01700-123456"],
                    "updated": "2 min ago"
                },
                {
                    "type": "drought",
                    "level": "MEDIUM",
                    "color": "#f59e0b",
                    "message_bn": ALERT_MESSAGES["drought"]["bn"],
                    "message_en": ALERT_MESSAGES["drought"]["en"],
                    "affected": ["Singra", "Naldanga"],
                    "actions": ["Conserve water", "Delay irrigation"],
                    "updated": "15 min ago"
                },
                {
                    "type": "rain",
                    "level": "MEDIUM",
                    "color": "#3b82f6",
                    "message_bn": ALERT_MESSAGES["rain"]["bn"],
                    "message_en": ALERT_MESSAGES["rain"]["en"],
                    "affected": ["Gurudaspur", "Lalpur"],
                    "actions": ["Stay indoors", "Clear drainage"],
                    "updated": "5 min ago"
                },
                {
                    "type": "lightning",
                    "level": "HIGH",
                    "color": "#eab308",
                    "message_bn": ALERT_MESSAGES["lightning"]["bn"],
                    "message_en": ALERT_MESSAGES["lightning"]["en"],
                    "affected": ["Lalpur", "Atrai"],
                    "actions": ["Avoid open fields", "Stay in concrete buildings"],
                    "updated": "1 min ago"
                },
                {
                    "type": "earthquake",
                    "level": "LOW",
                    "color": "#22c55e",
                    "message_bn": "এখন ভূমিকম্পের কোনো সতর্কতা নেই।",
                    "message_en": "No earthquake risk at this time.",
                    "affected": [],
                    "actions": ["No action required"],
                    "updated": "1 hr ago"
                },
            ]
        })


    @app.route('/api/alerts/simulate/<alert_type>', methods=['POST'])
    def simulate_alert(alert_type):
        """
        Simulate an alert and optionally send SMS.
        POST body: { "send_sms": true, "area": "Natore Sadar" }
        """
        if alert_type not in ALERT_MESSAGES:
            return jsonify({"error": f"Unknown alert type: {alert_type}"}), 400

        data     = request.get_json(silent=True) or {}
        do_sms   = data.get("send_sms", False)
        area     = data.get("area", "All Natore")

        result = {
            "alert_type": alert_type,
            "area":       area,
            "level":      "HIGH" if alert_type in ("flood", "lightning") else "MEDIUM",
            "message_bn": ALERT_MESSAGES[alert_type]["bn"],
            "timestamp":  datetime.datetime.utcnow().isoformat() + "Z",
            "sms_result": None,
        }

        if do_sms:
            sms_result = send_bulk_sms(REGISTERED_NUMBERS, alert_type)
            result["sms_result"] = sms_result

        return jsonify(result)


    # ── SMS APIs ──────────────────────────────────────────────────────

    @app.route('/api/sms/send', methods=['POST'])
    def api_send_sms():
        """
        Send a single SMS.
        Body: { "to": "+8801711234567", "type": "flood", "lang": "bn" }
        """
        data     = request.get_json()
        to       = data.get("to")
        typ      = data.get("type", "flood")
        lang     = data.get("lang", "bn")
        custom   = data.get("message")

        if not to:
            return jsonify({"error": "Missing 'to' field"}), 400

        message  = custom or ALERT_MESSAGES.get(typ, {}).get(lang, "সতর্কতা! —LMEWS")
        result   = send_sms(to, message, alert_type=typ)
        return jsonify(result)


    @app.route('/api/sms/bulk', methods=['POST'])
    def api_send_bulk():
        """
        Send bulk SMS to registered users.
        Body: { "type": "flood", "lang": "bn", "numbers": [...optional override...] }
        """
        data     = request.get_json()
        typ      = data.get("type", "flood")
        lang     = data.get("lang", "bn")
        numbers  = data.get("numbers", REGISTERED_NUMBERS)

        result   = send_bulk_sms(numbers, typ, lang)
        return jsonify(result)


    @app.route('/api/sms/log')
    def api_sms_log():
        limit  = int(request.args.get("limit", 50))
        return jsonify({"log": get_sms_log(limit), "stats": get_sms_stats()})


    @app.route('/api/sms/stats')
    def api_sms_stats():
        return jsonify(get_sms_stats())


    # ── Environmental Data APIs ───────────────────────────────────────
    # These simulate Google Earth Engine / weather API responses.
    # Replace with real GEE + API calls in production.

    @app.route('/api/data/ndvi')
    def api_ndvi():
        """Simulated NDVI data for Natore District upazilas."""
        return jsonify({
            "source":    "Google Earth Engine (Simulated)",
            "product":   "MODIS/006/MOD13Q1",
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "district":  "Natore",
            "mean":      0.62,
            "min":       0.18,
            "max":       0.84,
            "upazilas": [
                {"name": u, "ndvi": round(random.uniform(0.35, 0.82), 3)}
                for u in UPAZILAS
            ],
            "trend": "declining",  # compared to same period last year
            "interpretation": "Moderate vegetation stress — drought conditions possible"
        })


    @app.route('/api/data/ndwi')
    def api_ndwi():
        """Simulated NDWI (water index) data."""
        return jsonify({
            "source":    "Google Earth Engine (Simulated)",
            "product":   "LANDSAT/LC08",
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "district":  "Natore",
            "mean":      0.31,
            "flood_risk_zones": [
                {"upazila": "Natore Sadar", "ndwi": 0.48, "risk": "HIGH"},
                {"upazila": "Baraigram",    "ndwi": 0.52, "risk": "HIGH"},
                {"upazila": "Gurudaspur",   "ndwi": 0.29, "risk": "MEDIUM"},
                {"upazila": "Singra",       "ndwi": 0.18, "risk": "LOW"},
            ]
        })


    @app.route('/api/data/weather')
    def api_weather():
        """Simulated weather forecast data."""
        return jsonify({
            "source":      "BMD + OpenWeatherMap (Simulated)",
            "location":    "Natore, Rajshahi, Bangladesh",
            "timestamp":   datetime.datetime.utcnow().isoformat() + "Z",
            "current": {
                "temp_c":         32,
                "humidity_pct":   85,
                "wind_kmh":       24,
                "condition":      "Thunderstorms developing",
                "rainfall_mm":    12.4,
            },
            "forecast_6hr": {
                "rainfall_mm":    85,
                "lightning_risk": "HIGH",
                "wind_kmh":       38,
            },
            "flood_threshold_mm": 60,
            "alert_triggered":    True,
        })


    @app.route('/api/data/soil')
    def api_soil():
        """Simulated soil moisture data."""
        return jsonify({
            "source":     "NASA SMAP (Simulated)",
            "timestamp":  datetime.datetime.utcnow().isoformat() + "Z",
            "district":   "Natore",
            "mean_pct":   18.3,
            "threshold":  25.0,
            "status":     "BELOW_THRESHOLD",
            "upazilas": [
                {"name": u, "moisture_pct": round(random.uniform(12, 30), 1)}
                for u in UPAZILAS
            ]
        })


    @app.route('/api/data/lulc')
    def api_lulc():
        """Simulated Land Use / Land Cover classification."""
        return jsonify({
            "source":     "Google Earth Engine (Simulated)",
            "product":    "ESA WorldCover 2021",
            "timestamp":  datetime.datetime.utcnow().isoformat() + "Z",
            "district":   "Natore",
            "classes": {
                "cropland":    62.4,
                "built_up":    8.7,
                "wetland":     11.2,
                "water":       9.8,
                "vegetation":  5.4,
                "barren":      2.5,
            }
        })


    # ── Volunteer APIs ────────────────────────────────────────────────

    @app.route('/api/volunteers')
    def api_volunteers():
        """List of registered volunteers."""
        return jsonify({
            "total":  18,
            "active": 12,
            "volunteers": [
                {"name": "Rahman A.",  "upazila": "Natore Sadar", "phone": "0171-XXXXXX", "status": "active",  "task": "Door-to-door alerts"},
                {"name": "Khatun S.", "upazila": "Baraigram",    "phone": "0181-XXXXXX", "status": "active",  "task": "Shelter coordination"},
                {"name": "Hossain M.","upazila": "Gurudaspur",   "phone": "0191-XXXXXX", "status": "standby", "task": "River monitoring"},
                {"name": "Begum R.",  "upazila": "Lalpur",       "phone": "0171-XXXXXX", "status": "active",  "task": "SMS relay network"},
                {"name": "Islam F.",  "upazila": "Singra",       "phone": "0181-XXXXXX", "status": "offline", "task": None},
            ]
        })


    @app.route('/api/volunteers/alert', methods=['POST'])
    def alert_volunteers():
        """Send SMS to all active volunteers."""
        data     = request.get_json()
        typ      = data.get("type", "flood")
        vol_nums = ["+8801711111001", "+8801812222002", "+8801913333003"]
        result   = send_bulk_sms(vol_nums, typ, lang="bn")
        result["recipients"] = "volunteers"
        return jsonify(result)
