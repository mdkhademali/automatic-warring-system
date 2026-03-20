"""
Last-Mile Early Warning System (LMEWS)
Flask Backend — Main Application

Run: python app.py
API: http://localhost:5000
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import json, os, datetime, logging

from routes import register_routes
from sms import send_sms, get_sms_log

# ── App Setup ─────────────────────────────────────────────────────────
app = Flask(__name__)
CORS(app)  # Allow frontend on different port

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Register all route blueprints
register_routes(app)


# ── Root ──────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return jsonify({
        "system": "LMEWS — Last-Mile Early Warning System",
        "version": "1.0.0",
        "district": "Natore, Bangladesh",
        "status": "operational",
        "endpoints": [
            "/api/status",
            "/api/alerts",
            "/api/alerts/simulate/<type>",
            "/api/sms/send",
            "/api/sms/log",
            "/api/data/ndvi",
            "/api/data/ndwi",
            "/api/data/weather",
            "/api/data/soil",
            "/api/volunteers",
        ]
    })


# ── System Status ─────────────────────────────────────────────────────
@app.route('/api/status')
def system_status():
    return jsonify({
        "status": "operational",
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "services": {
            "sms_gateway":    "simulated",
            "gee_data":       "simulated",
            "weather_api":    "simulated",
            "volunteer_net":  "active",
        },
        "coverage": {
            "upazilas": 7,
            "registered_numbers": 8240,
            "active_volunteers": 12,
        }
    })


# ── Run ───────────────────────────────────────────────────────────────
if __name__ == '__main__':
    logger.info("🚨 LMEWS Backend starting — Natore District, Bangladesh")
    app.run(debug=True, host='0.0.0.0', port=5000)
