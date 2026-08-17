import sqlite3
import json
import os
import requests

# Detect Vercel / Serverless Environment
IS_SERVERLESS = bool(os.getenv('VERCEL') or os.getenv('AWS_LAMBDA_FUNCTION_NAME') or os.getenv('SERVERLESS'))
if IS_SERVERLESS:
    DB_PATH = '/tmp/scamshield.db'
else:
    DB_PATH = os.path.join(os.path.dirname(__file__), 'scamshield.db')

SCHEMA_PATH = os.path.join(os.path.dirname(__file__), 'schema.sql')

# Cloudflare D1 Environment Configuration
CLOUDFLARE_D1_ACCOUNT_ID = os.getenv('CLOUDFLARE_D1_ACCOUNT_ID')
CLOUDFLARE_D1_DATABASE_ID = os.getenv('CLOUDFLARE_D1_DATABASE_ID')
CLOUDFLARE_API_TOKEN = os.getenv('CLOUDFLARE_API_TOKEN')

def is_d1_configured():
    """Check if Cloudflare D1 REST API environment variables are present."""
    return bool(CLOUDFLARE_D1_ACCOUNT_ID and CLOUDFLARE_D1_DATABASE_ID and CLOUDFLARE_API_TOKEN)

def execute_d1_query(sql, params=None):
    """Execute SQL query against Cloudflare D1 REST API in production."""
    url = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_D1_ACCOUNT_ID}/d1/database/{CLOUDFLARE_D1_DATABASE_ID}/query"
    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "sql": sql,
        "params": params or []
    }
    response = requests.post(url, headers=headers, json=payload, timeout=10)
    data = response.json()
    if not data.get('success'):
        raise Exception(f"D1 Query Error: {data.get('errors')}")
    result_set = data.get('result', [{}])[0]
    return result_set.get('results', [])

def get_db_connection():
    """Establish connection to local SQLite database with sqlite3.Row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database tables using schema.sql."""
    if is_d1_configured():
        try:
            with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            for stmt in schema_sql.split(';'):
                if stmt.strip():
                    execute_d1_query(stmt.strip())
            execute_d1_query("INSERT OR IGNORE INTO user_stats (id, awareness_score, total_scans) VALUES (1, 85, 0)")
            return
        except Exception as e:
            print(f"Cloudflare D1 init error, falling back to SQLite: {e}")

    conn = get_db_connection()
    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        conn.executescript(f.read())
    
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM user_stats")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO user_stats (awareness_score, total_scans) VALUES (85, 0)")
    
    conn.commit()
    conn.close()

def save_scan(scan_type, risk_score, risk_level, scam_category, short_result, 
              warning_signs, explanation, recommended_actions, suspicious_phrases, input_summary):
    """Save scan analysis result into database securely."""
    summary_text = input_summary[:150] if input_summary else ""
    warning_json = json.dumps(warning_signs or [])
    rec_json = json.dumps(recommended_actions or [])
    phrase_json = json.dumps(suspicious_phrases or [])

    if is_d1_configured():
        try:
            sql = '''
                INSERT INTO scans (
                    scan_type, risk_score, risk_level, scam_category, short_result,
                    warning_signs_json, explanation, recommended_actions_json,
                    suspicious_phrases_json, input_summary
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            params = [scan_type, int(risk_score), risk_level, scam_category, short_result, warning_json, explanation, rec_json, phrase_json, summary_text]
            execute_d1_query(sql, params)
            execute_d1_query("UPDATE user_stats SET total_scans = total_scans + 1, updated_at = CURRENT_TIMESTAMP WHERE id = 1")
            
            # Fetch last row id
            rows = execute_d1_query("SELECT MAX(id) as id FROM scans")
            return rows[0]['id'] if rows else 1
        except Exception as e:
            print(f"D1 save scan error, falling back to SQLite: {e}")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO scans (
            scan_type, risk_score, risk_level, scam_category, short_result,
            warning_signs_json, explanation, recommended_actions_json,
            suspicious_phrases_json, input_summary
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (scan_type, int(risk_score), risk_level, scam_category, short_result, warning_json, explanation, rec_json, phrase_json, summary_text))
    
    scan_id = cursor.lastrowid
    cursor.execute("UPDATE user_stats SET total_scans = total_scans + 1, updated_at = CURRENT_TIMESTAMP WHERE id = 1")
    conn.commit()
    conn.close()
    return scan_id

def get_all_scans(limit=100, search="", filter_risk="", sort_by="newest"):
    """Retrieve scan history with search, filtering, and sorting."""
    if is_d1_configured():
        try:
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

            rows = execute_d1_query(query, params)
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
                    'warning_signs': json.loads(r.get('warning_signs_json') or '[]'),
                    'explanation': r.get('explanation', ''),
                    'recommended_actions': json.loads(r.get('recommended_actions_json') or '[]'),
                    'suspicious_phrases': json.loads(r.get('suspicious_phrases_json') or '[]'),
                    'input_summary': r.get('input_summary', '')
                })
            return results
        except Exception as e:
            print(f"D1 get_all_scans error, falling back to SQLite: {e}")

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
    if is_d1_configured():
        try:
            rows = execute_d1_query("SELECT * FROM scans WHERE id = ?", [scan_id])
            if not rows:
                return None
            r = rows[0]
            return {
                'id': r['id'],
                'created_at': r['created_at'],
                'scan_type': r['scan_type'],
                'risk_score': r['risk_score'],
                'risk_level': r['risk_level'],
                'scam_category': r['scam_category'],
                'short_result': r['short_result'],
                'warning_signs': json.loads(r.get('warning_signs_json') or '[]'),
                'explanation': r.get('explanation', ''),
                'recommended_actions': json.loads(r.get('recommended_actions_json') or '[]'),
                'suspicious_phrases': json.loads(r.get('suspicious_phrases_json') or '[]'),
                'input_summary': r.get('input_summary', '')
            }
        except Exception as e:
            print(f"D1 get_scan_by_id error, falling back to SQLite: {e}")

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
    if is_d1_configured():
        try:
            execute_d1_query("DELETE FROM scans WHERE id = ?", [scan_id])
            return True
        except Exception as e:
            print(f"D1 delete scan error, falling back to SQLite: {e}")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM scans WHERE id = ?", (scan_id,))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0

def save_quiz_result(score, total_questions, accuracy, difficulty="Medium"):
    """Save quiz results and dynamically recalculate scam awareness score."""
    new_awareness = min(100, max(50, int(accuracy * 0.4 + 60)))
    if is_d1_configured():
        try:
            execute_d1_query("INSERT INTO quiz_results (score, total_questions, accuracy, difficulty) VALUES (?, ?, ?, ?)", [score, total_questions, accuracy, difficulty])
            execute_d1_query("UPDATE user_stats SET awareness_score = ?, updated_at = CURRENT_TIMESTAMP WHERE id = 1", [new_awareness])
            return new_awareness
        except Exception as e:
            print(f"D1 save quiz error, falling back to SQLite: {e}")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO quiz_results (score, total_questions, accuracy, difficulty)
        VALUES (?, ?, ?, ?)
    ''', (score, total_questions, accuracy, difficulty))
    cursor.execute("UPDATE user_stats SET awareness_score = ?, updated_at = CURRENT_TIMESTAMP WHERE id = 1", (new_awareness,))
    conn.commit()
    conn.close()
    return new_awareness

def get_dashboard_analytics():
    """Retrieve full aggregated stats for Chart.js rendering."""
    if is_d1_configured():
        try:
            risk_rows = execute_d1_query("SELECT risk_level, COUNT(*) as count FROM scans GROUP BY risk_level")
            risk_counts = {'LIKELY SAFE': 0, 'NEEDS VERIFICATION': 0, 'SUSPICIOUS': 0, 'HIGH RISK': 0}
            for r in risk_rows:
                if r['risk_level'] in risk_counts:
                    risk_counts[r['risk_level']] = r['count']

            cat_rows = execute_d1_query("SELECT scam_category, COUNT(*) as count FROM scans GROUP BY scam_category ORDER BY count DESC LIMIT 8")
            categories = [{'category': r['scam_category'], 'count': r['count']} for r in cat_rows]

            total_rows = execute_d1_query("SELECT COUNT(*) as total FROM scans")
            total_scans = total_rows[0]['total'] if total_rows else 0

            stat_rows = execute_d1_query("SELECT awareness_score FROM user_stats WHERE id = 1")
            awareness_score = stat_rows[0]['awareness_score'] if stat_rows else 85

            recent_rows = execute_d1_query("SELECT * FROM scans ORDER BY created_at DESC LIMIT 5")
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
            return {
                'total_scans': total_scans,
                'awareness_score': awareness_score,
                'risk_counts': risk_counts,
                'categories': categories,
                'recent_scans': recent_scans
            }
        except Exception as e:
            print(f"D1 get_dashboard_analytics error, falling back to SQLite: {e}")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT risk_level, COUNT(*) as count FROM scans GROUP BY risk_level")
    risk_rows = cursor.fetchall()
    risk_counts = {'LIKELY SAFE': 0, 'NEEDS VERIFICATION': 0, 'SUSPICIOUS': 0, 'HIGH RISK': 0}
    for r in risk_rows:
        if r['risk_level'] in risk_counts:
            risk_counts[r['risk_level']] = r['count']

    cursor.execute("SELECT scam_category, COUNT(*) as count FROM scans GROUP BY scam_category ORDER BY count DESC LIMIT 8")
    cat_rows = cursor.fetchall()
    categories = [{'category': r['scam_category'], 'count': r['count']} for r in cat_rows]

    cursor.execute("SELECT COUNT(*) FROM scans")
    total_scans = cursor.fetchone()[0]

    cursor.execute("SELECT awareness_score FROM user_stats WHERE id = 1")
    stat_row = cursor.fetchone()
    awareness_score = stat_row['awareness_score'] if stat_row else 85

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
