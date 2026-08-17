# ScamShield 🛡️

> **"Don't Trust It. Check It."**  
> AI-Powered Cyber Safety & Scam Awareness Platform

ScamShield is a complete, production-grade cybersecurity platform built to help non-technical users and families analyze suspicious **SMS, WhatsApp messages, Emails, Web URLs, Screenshots, Call Transcripts, and Audio Recordings** for potential fraud before they put their money or personal information at risk.

---

## ☁️ Cloudflare Deployment Architecture

```
                       ┌─────────────────────────────────────┐
                       │          User Browser / App         │
                       └──────────────────┬──────────────────┘
                                          │
                                          ▼
                       ┌─────────────────────────────────────┐
                       │        Cloudflare Global CDN        │
                       │     (Pages / Workers Edge Rules)    │
                       └──────────┬────────────────┬─────────┘
                                  │                │
                    Static Assets │                │ API / WSGI Requests
                                  ▼                ▼
                       ┌────────────────┐ ┌──────────────────┐
                       │ Static Assets  │ │ Python WSGI      │
                       │  (/static/*)   │ │ Worker Engine    │
                       └────────────────┘ └────────┬─────────┘
                                                   │
                                ┌──────────────────┼──────────────────┐
                                │                  │                  │
                                ▼                  ▼                  ▼
                       ┌────────────────┐ ┌────────────────┐ ┌────────────────┐
                       │ Cloudflare D1  │ │ Cloudflare R2  │ │ Multi-Tier OCR │
                       │ Serverless DB  │ │ Object Storage │ │ & Risk Engine  │
                       └────────────────┘ └────────────────┘ └────────────────┘
```

---

## 🛠️ Cloudflare Services Used

- **Cloudflare Pages / Workers**: Serves static assets (`/static/`) via Cloudflare's global edge network.
- **Python WSGI Worker Engine (`worker.py` / `wsgi.py`)**: Executes Python Flask application routing, risk engine calculations, and analysis endpoints.
- **Cloudflare D1 (`database/database.py`)**: Serverless SQL database storing scan history, risk scores, quiz progress, and awareness scores with automatic local SQLite fallback.
- **Cloudflare R2 Storage**: Object storage for secure screenshot and audio byte streams.
- **Multi-Tier OCR Engine (`utils/ocr.py`)**: In-memory screenshot processing via local Pytesseract, Cloud OCR API, or pattern fallback extractor.

---

## 🔑 Required Environment Variables

| Variable | Required | Default Value | Description |
|---|---|---|---|
| `FLASK_ENV` | Yes | `production` | Production environment flag |
| `DEBUG` | Yes | `False` | Disables debug mode in production |
| `SECRET_KEY` | Yes | `(Generated Secret)` | Flask session encryption key |
| `AI_PROVIDER` | No | `rule_based` | Analysis engine provider (`rule_based` or `ai_powered`) |
| `CLOUDFLARE_D1_ACCOUNT_ID` | Production | `""` | Cloudflare Account ID for D1 SQL API |
| `CLOUDFLARE_D1_DATABASE_ID` | Production | `""` | Cloudflare D1 Database ID |
| `CLOUDFLARE_API_TOKEN` | Production | `""` | Cloudflare API Bearer Token |
| `OCR_SPACE_API_KEY` | Optional | `""` | Optional Cloud OCR API Key |

---

## 🚀 Deployment Instructions for Cloudflare

### Method 1: Deploy via Wrangler CLI (Recommended)

1. **Install Wrangler CLI**:
   ```bash
   npm install -g wrangler
   ```

2. **Login to Cloudflare**:
   ```bash
   wrangler login
   ```

3. **Create Cloudflare D1 Database**:
   ```bash
   wrangler d1 create scamshield-db
   ```
   *Copy the generated `database_id` into your `wrangler.toml` file.*

4. **Initialize D1 Schema**:
   ```bash
   wrangler d1 execute scamshield-db --file=./database/schema.sql
   ```

5. **Create Cloudflare R2 Storage Bucket**:
   ```bash
   wrangler r2 bucket create scamshield-uploads
   ```

6. **Deploy Application to Cloudflare**:
   ```bash
   wrangler deploy
   ```

---

### Method 2: Deploy via Cloudflare Pages + GitHub Integration

1. Connect your GitHub repository: [`https://github.com/Amansrivastav2004/ScamShield-`](https://github.com/Amansrivastav2004/ScamShield-) to **Cloudflare Pages**.
2. Set Build Command: `pip install -r requirements.txt`
3. Set Output Directory: `static`
4. Add Environment Variables in Cloudflare Dashboard:
   - `FLASK_ENV`: `production`
   - `DEBUG`: `False`
   - `SECRET_KEY`: `<your-random-secret-key>`

---

## 💻 Local Development Setup

1. **Clone repository**:
   ```bash
   git clone https://github.com/Amansrivastav2004/ScamShield-.git
   cd ScamShield-
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run local development server**:
   ```bash
   python app.py
   ```
   *Access local server at `http://127.0.0.1:5000`*

4. **Run automated test suite**:
   ```bash
   python -m unittest discover tests
   ```

---

## 📱 Mobile App Integration

- **Android App**: Pre-configured in [`ScamShieldApp/`](./ScamShieldApp/). Open in Android Studio and build APK.
- **PWA (Progressive Web App)**: Open `http://127.0.0.1:5000` or production URL in mobile browser and tap **"Add to Home Screen"**.

---

© 2026 ScamShield. All rights reserved. *"Don't Trust It. Check It."*
