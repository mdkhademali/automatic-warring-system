## Last-Mile Early Warning System (LMEWS)
### Case Study: Natore District, Bangladesh

> *Bridging the gap between national disaster forecasts and last-mile vulnerable communities, even without internet.*

---

## Project Overview

LMEWS is an intelligent, production-quality early warning platform designed to deliver life-saving hazard alerts to the most vulnerable communities in rural Bangladesh. The system addresses the critical "last mile" problem: national disaster forecasting agencies generate accurate predictions, but this information rarely reaches the farmers, fishermen, and families who need it most, quickly enough, in their language, through channels they can access.

**Case Study District:** Natore, Rajshahi Division, 7 Upazilas, ~1.4 million residents, prone to flooding from the Atrai and Baral rivers, drought, lightning, and seasonal extreme weather.

---

## Features

### Interactive Map Dashboard
- Leaflet.js map centered on Natore District (24.41°N, 88.99°E)
- Risk markers for all 7 upazilas with color-coded risk levels
- Toggleable satellite-derived layers: **NDVI**, **NDWI**, **LULC**, **Soil Moisture**
- Dynamic flood zone polygon rendering on alert simulation
- Layer info panel with scientific explanations

### Early Warning System
- **5 hazard types:** Flood · Drought · Heavy Rainfall · Lightning · Earthquake
- Color-coded risk cards: 🟢 LOW · 🟡 MEDIUM · 🔴 HIGH
- Bangla (Bengali) messages for all alerts
- Action recommendations for each hazard
- Visual alert overlay with animation on simulation

### SMS Alert System (Key Feature)
- Full `send_sms()` and `send_bulk_sms()` backend functions
- **Twilio integration** — real SMS when API keys are set
- **Simulation mode** — works perfectly without any API keys
- Pre-written Bangla alert messages for all 5 hazard types
- Live SMS log with delivery status, timestamps, and phone numbers
- Bulk dispatch to 8,240+ registered numbers
- Delivery statistics: total sent, delivered, failed, reach rate

### Last-Mile Communication Panel
- Alert propagation chain: Satellite → Server → SMS → Voice → Volunteers → Community
- 6 communication channels: SMS, Voice Broadcast, Volunteer Relay, Drum/Siren, Community Radio, Offline Kiosks
- Each channel shows deployment status and coverage

### Analytics Dashboard (Chart.js)
- Monthly rainfall trend (12-month bar chart)
- NDVI vegetation health trend (line chart)
- Risk level distribution (doughnut chart)
- SMS delivery performance over time (multi-line chart)
- KPI cards: rainfall, NDVI mean, flood events, SMS alerts

### Coordination Panel
- 3-role task board: Authorities · Volunteers · Community members
- Volunteer roster with upazila, phone, status, and assignment
- Real-time task prioritization

### Offline Mode Concept
- Detailed breakdown of what works vs. what requires internet
- 5-step offline alert protocol using local sensors + GSM SMS
- Edge-device architecture for total internet-independence

### Dark / Light Mode
- Full theme toggle with smooth transition
- Glass-morphism UI panels adapt to both modes

### Community Mode
- Full-screen simplified UI for low-literacy users
- Large icons, minimal text, Bangla labels
- Giant color-coded alert status card
- Quick-access buttons: Shelter · Help · Water · Medical

### Alert Simulation
- "Flood Alert" button: triggers animated overlay on map + SMS log entry + toast
- "Lightning Alert" button: same flow with yellow styling
- Auto-dismiss after 8 seconds

---

## Tech Stack

| Layer     | Technology |
|-----------|------------|
| Frontend  | HTML5 · Tailwind CSS · Vanilla JavaScript |
| Map       | Leaflet.js 1.9.4 |
| Charts    | Chart.js 4.4 |
| Icons     | Lucide Icons |
| Backend   | Python · Flask 3.x |
| SMS       | Twilio (real) / Simulation fallback |
| Fonts     | Syne · IBM Plex Mono · Noto Sans Bengali |

---

## Setup Instructions

### Frontend Only (no backend needed)
1. Open `frontend/index.html` in any browser — or use VS Code Live Server
2. All map, chart, and SMS simulation features work without a backend

### Full Stack Setup

**1. Clone / unzip the project**
```bash
cd last-mile-ews
```

**2. Install Python dependencies**
```bash
cd backend
pip install -r requirements.txt
```

**3. (Optional) Configure Twilio for real SMS**
```bash
# Create .env file in /backend
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_FROM_NUMBER=+1234567890
```

**4. Run the backend**
```bash
python app.py
# → Running on http://0.0.0.0:5000
```

**5. Open the frontend**
- Open `frontend/index.html` with Live Server (VS Code extension)
- Or: `python -m http.server 8080` in the `/frontend` folder

---

## How SMS Works

### Simulation Mode (default — no setup needed)
When no Twilio credentials are set, `send_sms()` automatically falls back to simulation:
- Messages are logged to the in-memory SMS log
- All frontend SMS features work identically
- Dashboard shows "SIMULATED" status

### Real SMS Mode (Twilio)
1. Sign up at [twilio.com](https://twilio.com) and get a phone number
2. Set `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_FROM_NUMBER` in `.env`
3. Replace simulated numbers in `routes.py` with real registered numbers from your database
4. Call `POST /api/sms/bulk` with alert type to dispatch to all registered users

### SMS Flow
```
Alert Triggered
     ↓
POST /api/alerts/simulate/<type>?send_sms=true
     ↓
send_bulk_sms(registered_numbers, alert_type)
     ↓
For each number: send_sms(to, bangla_message)
     ↓
Twilio API → GSM Network → Recipient's phone
     ↓
Log entry created → Dashboard updated
```

### Example Bangla SMS
```
সতর্কতা: নাটোরে বন্যার সম্ভাবনা। দ্রুত নিরাপদ স্থানে যান। —LMEWS
```
*(Translation: WARNING: Flood risk in Natore. Move to safe location immediately. —LMEWS)*

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/status` | System health check |
| GET | `/api/alerts` | All current alert levels |
| POST | `/api/alerts/simulate/<type>` | Trigger alert simulation |
| POST | `/api/sms/send` | Send single SMS |
| POST | `/api/sms/bulk` | Send bulk SMS |
| GET | `/api/sms/log` | SMS delivery log |
| GET | `/api/sms/stats` | Delivery statistics |
| GET | `/api/data/ndvi` | NDVI vegetation data |
| GET | `/api/data/ndwi` | Water index data |
| GET | `/api/data/weather` | Weather forecast |
| GET | `/api/data/soil` | Soil moisture data |
| GET | `/api/data/lulc` | Land use classification |
| GET | `/api/volunteers` | Volunteer roster |
| POST | `/api/volunteers/alert` | Alert all volunteers |

---

## How to Connect Real APIs

### Google Earth Engine (NDVI, NDWI, LULC, Soil Moisture)
```python
# Install: pip install earthengine-api
import ee
ee.Authenticate()
ee.Initialize(project='your-gee-project')

# Example: Get NDVI for Natore
geometry = ee.Geometry.Rectangle([88.75, 24.20, 89.25, 24.75])
ndvi = ee.ImageCollection('MODIS/006/MOD13Q1') \
         .filterDate('2025-01-01', '2025-06-01') \
         .select('NDVI') \
         .mean() \
         .reduceRegion(ee.Reducer.mean(), geometry, 500)
print(ndvi.getInfo())
```
Replace the `/api/data/ndvi` route in `routes.py` with real GEE calls.

### Bangladesh Meteorological Department (BMD) / Open-Meteo
```python
import requests
# Open-Meteo (free, no key needed)
url = "https://api.open-meteo.com/v1/forecast"
params = { "latitude": 24.41, "longitude": 88.99, "hourly": "precipitation,temperature_2m" }
data = requests.get(url, params=params).json()
```

### Twilio SMS (already integrated)
```python
# Just set environment variables:
TWILIO_ACCOUNT_SID = "ACxxx..."
TWILIO_AUTH_TOKEN  = "your_token"
TWILIO_FROM_NUMBER = "+1xxxxxxxxxx"
# send_sms() will auto-use real Twilio when these are set
```

---

## Why LMEWS Wins at Last-Mile Delivery

| Challenge | LMEWS Solution |
|-----------|----------------|
| No internet in villages | SMS via basic GSM (2G) — always works |
| Low literacy | Community Mode with icons + Bangla |
| Power outages | Offline edge device + drum/siren protocol |
| Language barrier | All alerts in Bangla (native language) |
| Slow information flow | Volunteer network for door-to-door relay |
| National data not localized | Upazila-level risk mapping |

---

## Future Improvements

1. **AI Prediction Model** — LSTM/GRU model trained on 10-year flood data for Natore
2. **WhatsApp Integration** — Twilio WhatsApp API for richer alerts with images
3. **IVR Voice Calls** — Auto-dialed Bangla voice alerts for non-literate users
4. **Mobile App** — Flutter app for volunteers with offline-first sync
5. **IoT River Gauges** — ESP32 sensors at riverbanks sending real-time levels
6. **Community Feedback** — SMS reply "1=SAFE 2=NEED HELP" for 2-way communication
7. **Satellite Phone Backup** — Iridium/Inmarsat for total communication blackout
8. **Solar Kiosks** — Offline alert display boards at Union Parishad offices
9. **Multi-language** — Chakma, Santhali for indigenous communities
10. **National Integration** — Connect to BWDB flood forecasting API

---

## Contact & Credits

- **System:** LMEWS v1.0 — Mapathon Competition Entry
- **Focus Area:** Natore District, Rajshahi Division, Bangladesh
- **Data Sources:** MODIS, Landsat-8, SMAP NASA, BMD (simulated for demo)
- **SMS Provider:** Twilio (simulation mode by default)

---

*"The last mile is not a technology problem — it is a human and language problem. LMEWS solves both."*
