import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'scamshield.db')
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), 'schema.sql')

def get_db_connection():
    """Establish connection to SQLite database with sqlite3.Row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database tables using schema.sql."""
    conn = get_db_connection()
    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        conn.executescript(f.read())
    
    # Initialize default user stats if empty
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM user_stats")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO user_stats (awareness_score, total_scans) VALUES (85, 0)")
    
    conn.commit()
    conn.close()

def save_scan(scan_type, risk_score, risk_level, scam_category, short_result, 
              warning_signs, explanation, recommended_actions, suspicious_phrases, input_summary):
    """Save scan analysis result into database securely."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO scans (
            scan_type, risk_score, risk_level, scam_category, short_result,
            warning_signs_json, explanation, recommended_actions_json,
            suspicious_phrases_json, input_summary
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        scan_type,
        int(risk_score),
        risk_level,
        scam_category,
        short_result,
        json.dumps(warning_signs or []),
        explanation,
        json.dumps(recommended_actions or []),
        json.dumps(suspicious_phrases or []),
        input_summary[:150] if input_summary else ""
    ))
    
    scan_id = cursor.lastrowid
    
    # Update total scan count
    cursor.execute("UPDATE user_stats SET total_scans = total_scans + 1, updated_at = CURRENT_TIMESTAMP WHERE id = 1")
    
    conn.commit()
    conn.close()
    return scan_id

def get_all_scans(limit=100, search="", filter_risk="", sort_by="newest"):
    """Retrieve scan history with search, filtering, and sorting."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM scans WHERE 1=1"
    params = []
    
    if search:
        query += " AND (scam_category LIKE ? OR short_result LIKE ? OR input_summary LIKE ? OR scan_type LIKE ?)"
        term = f"%{search}%"
        params.extend([term, term, term, term])
        
    if filter_risk:
        query += " AND risk_level = ?"
        params.append(filter_risk)
        
    if sort_by == "oldest":
        query += " ORDER BY created_at ASC"
    elif sort_by == "risk_high":
        query += " ORDER BY risk_score DESC, created_at DESC"
    elif sort_by == "risk_low":
        query += " ORDER BY risk_score ASC, created_at DESC"
    else:
        query += " ORDER BY created_at DESC"
        
    query += " LIMIT ?"
    params.append(limit)
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    results = []
    for r in rows:
        results.append({
            'id': r['id'],
            'created_at': r['created_at'],
            'scan_type': r['scan_type'],
            'risk_score': r['risk_score'],
            'risk_level': r['risk_level'],
            'scam_category': r['scam_category'],
            'short_result': r['short_result'],
            'warning_signs': json.loads(r['warning_signs_json'] or '[]'),
            'explanation': r['explanation'],
            'recommended_actions': json.loads(r['recommended_actions_json'] or '[]'),
            'suspicious_phrases': json.loads(r['suspicious_phrases_json'] or '[]'),
            'input_summary': r['input_summary']
        })
        
    conn.close()
    return results

def get_scan_by_id(scan_id):
    """Fetch single scan detail by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM scans WHERE id = ?", (scan_id,))
    r = cursor.fetchone()
    conn.close()
    
    if not r:
        return None
        
    return {
        'id': r['id'],
        'created_at': r['created_at'],
        'scan_type': r['scan_type'],
        'risk_score': r['risk_score'],
        'risk_level': r['risk_level'],
        'scam_category': r['scam_category'],
        'short_result': r['short_result'],
        'warning_signs': json.loads(r['warning_signs_json'] or '[]'),
        'explanation': r['explanation'],
        'recommended_actions': json.loads(r['recommended_actions_json'] or '[]'),
        'suspicious_phrases': json.loads(r['suspicious_phrases_json'] or '[]'),
        'input_summary': r['input_summary']
    }

def delete_scan_by_id(scan_id):
    """Delete a scan record from history."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM scans WHERE id = ?", (scan_id,))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0

def save_quiz_result(score, total_questions, accuracy, difficulty="Medium"):
    """Save quiz results and dynamically recalculate scam awareness score."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO quiz_results (score, total_questions, accuracy, difficulty)
        VALUES (?, ?, ?, ?)
    ''', (score, total_questions, accuracy, difficulty))
    
    # Calculate awareness score boost based on quiz performance
    new_awareness = min(100, max(50, int(accuracy * 0.4 + 60)))
    cursor.execute("UPDATE user_stats SET awareness_score = ?, updated_at = CURRENT_TIMESTAMP WHERE id = 1", (new_awareness,))
    
    conn.commit()
    conn.close()
    return new_awareness

def get_dashboard_analytics():
    """Retrieve full aggregated stats for Chart.js rendering."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Risk Distribution
    cursor.execute("SELECT risk_level, COUNT(*) as count FROM scans GROUP BY risk_level")
    risk_rows = cursor.fetchall()
    risk_counts = {
        'LIKELY SAFE': 0,
        'NEEDS VERIFICATION': 0,
        'SUSPICIOUS': 0,
        'HIGH RISK': 0
    }
    for r in risk_rows:
        if r['risk_level'] in risk_counts:
            risk_counts[r['risk_level']] = r['count']
            
    # Scam Category Breakdown
    cursor.execute("SELECT scam_category, COUNT(*) as count FROM scans GROUP BY scam_category ORDER BY count DESC LIMIT 8")
    cat_rows = cursor.fetchall()
    categories = [{'category': r['scam_category'], 'count': r['count']} for r in cat_rows]
    
    # Total scans
    cursor.execute("SELECT COUNT(*) FROM scans")
    total_scans = cursor.fetchone()[0]
    
    # Awareness Score
    cursor.execute("SELECT awareness_score FROM user_stats WHERE id = 1")
    stat_row = cursor.fetchone()
    awareness_score = stat_row['awareness_score'] if stat_row else 85
    
    # Recent Scans
    cursor.execute("SELECT * FROM scans ORDER BY created_at DESC LIMIT 5")
    recent_rows = cursor.fetchall()
    recent_scans = []
    for r in recent_rows:
        recent_scans.append({
            'id': r['id'],
            'created_at': r['created_at'],
            'scan_type': r['scan_type'],
            'risk_score': r['risk_score'],
            'risk_level': r['risk_level'],
            'scam_category': r['scam_category'],
            'short_result': r['short_result']
        })
        
    conn.close()
    
    return {
        'total_scans': total_scans,
        'awareness_score': awareness_score,
        'risk_counts': risk_counts,
        'categories': categories,
        'recent_scans': recent_scans
    }
