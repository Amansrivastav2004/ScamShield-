-- ScamShield SQLite Database Schema

CREATE TABLE IF NOT EXISTS scans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    scan_type TEXT NOT NULL, -- 'message', 'url', 'screenshot', 'call'
    risk_score INTEGER NOT NULL, -- 0 to 100
    risk_level TEXT NOT NULL, -- 'LIKELY SAFE', 'NEEDS VERIFICATION', 'SUSPICIOUS', 'HIGH RISK'
    scam_category TEXT NOT NULL, -- 'Banking Scam', 'UPI Scam', 'KYC Scam', 'Phishing', etc.
    short_result TEXT,
    warning_signs_json TEXT, -- JSON array of warning strings
    explanation TEXT,
    recommended_actions_json TEXT, -- JSON array of recommendation strings
    suspicious_phrases_json TEXT, -- JSON array of highlighted phrases
    input_summary TEXT -- Truncated/sanitized summary of analyzed content
);

CREATE TABLE IF NOT EXISTS quiz_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    score INTEGER NOT NULL,
    total_questions INTEGER NOT NULL,
    accuracy REAL NOT NULL,
    difficulty TEXT DEFAULT 'Medium'
);

CREATE TABLE IF NOT EXISTS user_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    awareness_score INTEGER DEFAULT 85,
    total_scans INTEGER DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for fast query execution
CREATE INDEX IF NOT EXISTS idx_scans_created_at ON scans(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_scans_risk_level ON scans(risk_level);
CREATE INDEX IF NOT EXISTS idx_scans_category ON scans(scam_category);
