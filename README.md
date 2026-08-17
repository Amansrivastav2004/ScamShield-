# ScamShield 🛡️

> **"Don't Trust It. Check It."**  
> AI-Powered Cyber Safety & Scam Awareness Platform

ScamShield is a complete, production-grade cybersecurity platform built to help non-technical users and families analyze suspicious **SMS, WhatsApp messages, Emails, Web URLs, Screenshots, Call Transcripts, and Audio Recordings** for potential fraud before they put their money or personal information at risk.

---

## 🌟 Key Features

1. **Unified Scan Center**:
   - **💬 Message Scanner**: Detects fake KYC warnings, urgent payment demands, task scams, lottery claims, and credential requests.
   - **🔗 URL Checker**: Performs heuristic analysis on domain lookalikes, raw IP addresses, URL shorteners, missing HTTPS, and high-risk TLDs.
   - **📸 Screenshot Scanner (OCR)**: Uploads screenshots of chats or payment alerts, extracts text via **Tesseract OCR**, allows user text review/editing, and runs risk analysis.
   - **📞 Call / Audio Analyzer**: Detects authority impersonation (Police/CBI/TRAI), fake "Digital Arrest" threats, and remote access app demands (AnyDesk/TeamViewer).

2. **Transparent Risk Engine**:
   - Scores content from **0 to 100**.
   - Categorizes risk levels:
     - 🟢 **LIKELY SAFE** (0–24)
     - 🟡 **NEEDS VERIFICATION** (25–49)
     - 🟠 **SUSPICIOUS** (50–74)
     - 🔴 **HIGH RISK** (75–100)
   - Highlights red-flag suspicious text snippets directly inside the user content.
   - Clear disclaimer: *Results are risk assessments, not 100% fraud guarantees.*

3. **🚨 "What Should I Do Now?" Guidance**:
   - Context-sensitive, step-by-step action guides tailored to specific scam categories (KYC, UPI, Job, Remote Access, Impersonation).
   - Direct helpline reminders (1930 / cybercrime.gov.in).

4. **Analytics Dashboard**:
   - Visualized via **Chart.js**: Risk distribution pie chart, top scam categories bar chart, total scans counter, and recent scan logs.

5. **Scan History**:
   - SQLite-backed history tracking with search, risk filtering, sorting, view modal, and single/bulk record deletion.

6. **"Can You Spot The Scam?" Interactive Quiz Simulator**:
   - Multi-difficulty quiz questions with instant feedback and explanations.
   - Recalculates and tracks your **Scam Awareness Score (0–100 🛡️)**.

7. **Educational Safety Center**:
   - Knowledgebase covering OTP safety, UPI QR codes, Phishing links, Digital Arrest scams, WFH job scams, and AnyDesk remote access risks.

8. **Multilingual Support**:
   - Instant UI language switching between **English**, **Hindi (हिंदी)**, and **Hinglish**.

---

## 🛠️ Technology Stack

- **Frontend**: HTML5, Vanilla CSS3 (Custom Design System, Glassmorphism, Dark Theme), Vanilla JavaScript (ES6+).
- **Backend**: Python 3.12, Flask.
- **Database**: SQLite3.
- **Charts**: Chart.js.
- **OCR Engine**: Tesseract OCR (`pytesseract`, PIL/Pillow).
- **Architecture**: Modular Service Layer (`AIServiceAdapter`).

---

## 📁 Project Architecture & Folder Structure

```
ScamShield/
│
├── app.py                      # Flask Application Factory & Route Handlers
├── requirements.txt            # Python Dependencies
├── README.md                   # Technical Documentation
├── .env.example                # Environment Variable Template
├── .gitignore                  # Git Ignore Rules
│
├── database/
│   ├── database.py             # SQLite Connection Manager & Analytics Helpers
│   ├── schema.sql              # Database Tables & Index Definitions
│   └── scamshield.db           # SQLite Database Storage
│
├── templates/
│   ├── base.html               # Master Layout with Navbar & Footer
│   ├── index.html              # Landing Page
│   ├── scan.html               # Unified Scan Center Hub
│   ├── message_scan.html       # Message Scanner UI
│   ├── url_scan.html           # URL Scanner UI
│   ├── screenshot_scan.html    # Screenshot OCR Upload & Edit UI
│   ├── call_scan.html          # Call Transcript & Audio Upload UI
│   ├── result.html             # Animated Risk Meter & Analysis Report Page
│   ├── dashboard.html          # Chart.js Analytics Dashboard
│   ├── history.html            # SQLite Scan History Page
│   ├── quiz.html               # Interactive Quiz Simulator
│   └── safety_center.html      # Educational Knowledgebase
│
├── static/
│   ├── css/
│   │   ├── style.css           # Core Design System, Theme Tokens & Typography
│   │   ├── components.css      # Buttons, Risk Gauges, Modals, Toast Styles
│   │   └── responsive.css      # Mobile, Tablet & Desktop Responsive Rules
│   │
│   └── js/
│       ├── main.js             # Global Toast & Modal Controllers
│       ├── scan.js             # Form AJAX & SVG Gauge Renderer
│       ├── dashboard.js        # Chart.js Dashboard Visualizations
│       ├── quiz.js             # Quiz Game Engine & Awareness Score Sync
│       └── language.js         # Multilingual Translator (EN, HI, Hinglish)
│
├── uploads/                    # Temporary Secure Upload Storage
│
├── utils/
│   ├── risk_engine.py          # Rule-Based Risk Scoring Logic & Recommendations
│   ├── message_analyzer.py     # SMS, WhatsApp & Email Indicator Extractor
│   ├── url_analyzer.py         # Domain Heuristics & Link Analyzer
│   ├── ocr.py                  # Tesseract OCR & Fallback Text Extractor
│   ├── audio_transcriber.py    # Call Transcript & Audio Scam Pattern Detector
│   ├── ai_service.py           # AI Service Layer Abstraction Adapter
│   └── helpers.py              # File Validation, Demo Data Loader & Quiz Data
│
└── tests/
    └── test_scamshield.py      # Automated Unit & Route Test Suite
```

---

## ⚡ Quick Start & Installation

### 1. Clone or Open Project Folder
```bash
cd d:\Scamm
```

### 2. Create Virtual Environment (Optional but Recommended)
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Application
```bash
python app.py
```

### 5. Access in Browser
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🧪 Running Automated Tests

Run the included unittest suite to verify all routes, risk scoring rules, and database operations:
```bash
python -m unittest discover tests
```

---

## 🔒 Security & Privacy Practices

- **Zero Unnecessary Data Retention**: Full sensitive messages are never stored permanently.
- **Secure File Handling**: Input images and audio files are validated by extension and size (< 16MB), processed, and temporary files are automatically deleted.
- **No API Key Exposure**: All secrets are stored in server-side `.env` environment variables.
- **SQL Injection & XSS Protection**: All database queries use parameterized SQL bindings, and user content is HTML-escaped.

---

## ⚠️ Limitations & Disclaimers

1. **Risk Assessment Only**: Rule-based scam evaluation provides transparent risk scores based on known indicators. It is not a 100% guarantee of fraud or safety.
2. **Heuristic URL Scanning**: URL analysis checks domain syntax, shorteners, and IP patterns. Real-time threat intelligence requires external API keys (e.g. VirusTotal).
3. **OCR System**: Image text extraction relies on Tesseract OCR. Image clarity or stylized text can affect accuracy.
4. **Audio Transcription**: Audio file analysis uses pattern matching and speech recognition fallback if cloud speech APIs are unconfigured.

---

## 🚀 Future Enhancements

- Integration with VirusTotal / Google Safe Browsing APIs.
- AI LLM integration via `utils/ai_service.py` for multi-turn conversational scam advice.
- Mobile App / Browser Extension for automatic call & link warnings.

---

*Built with ❤️ for Cyber Safety & Awareness.*
