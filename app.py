import os
import re
import json
import io
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Load Environment Variables
load_dotenv()

# Define Absolute Base Directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if os.path.exists(os.path.join(BASE_DIR, 'public', 'static')):
    STATIC_DIR = os.path.join(BASE_DIR, 'public', 'static')
else:
    STATIC_DIR = os.path.join(BASE_DIR, 'static')
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')

# Import Database & Utility Services
from database.database import (
    init_db, save_scan, get_all_scans, get_scan_by_id, 
    delete_scan_by_id, get_dashboard_analytics, save_quiz_result
)
from utils.ai_service import ai_service
from utils.ocr import extract_text_from_image
from utils.audio_transcriber import transcribe_audio_file
from utils.helpers import (
    allowed_file, sanitize_input, get_demo_examples, 
    get_quiz_questions, get_safety_articles
)

# Initialize Flask Application with Explicit Absolute Paths
app = Flask(
    __name__, 
    root_path=BASE_DIR,
    static_folder=STATIC_DIR, 
    static_url_path='/static',
    template_folder=TEMPLATE_DIR
)
app.secret_key = os.getenv('SECRET_KEY', 'scamshield_super_secret_cyber_security_key_2026')

if os.getenv('VERCEL'):
    app.config['UPLOAD_FOLDER'] = '/tmp/uploads'
else:
    app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'uploads')

# Explicit Static File Route for Vercel Serverless Functions
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(STATIC_DIR, filename)

class VercelPathMiddleware:
    """WSGI Middleware to restore original request PATH_INFO on Vercel Serverless Function rewrites."""
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        matched_path = (
            environ.get('HTTP_X_FORWARDED_URI') or 
            environ.get('HTTP_X_MATCHED_PATH') or 
            environ.get('HTTP_X_ORIGINAL_URI') or 
            environ.get('HTTP_X_VERCEL_FORWARDED_PATH') or
            environ.get('RAW_URI')
        )
        if matched_path and not matched_path.startswith('/static/'):
            clean_path = matched_path.split('?')[0]
            if clean_path and clean_path not in ['/api/index', '/api/index.py']:
                environ['PATH_INFO'] = clean_path
        return self.app(environ, start_response)

app.wsgi_app = VercelPathMiddleware(app.wsgi_app)

@app.route('/api/index')
@app.route('/api/index.py')
def vercel_index_fallback():
    """Fallback route if Vercel passes /api/index directly."""
    return home()

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB Max Upload Limit

# Ensure Uploads folder exists
try:
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
except Exception:
    pass

# Initialize Database Schema on Start
with app.app_context():
    init_db()

# Security Headers & CORS Middleware
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

# Helper to format text highlighting for red flags
def apply_phrase_highlights(text, suspicious_phrases):
    if not text or not suspicious_phrases:
        return text
    highlighted = text
    for phrase in suspicious_phrases:
        if phrase and len(phrase.strip()) > 2:
            try:
                pattern = re.compile(re.escape(phrase), re.IGNORECASE)
                highlighted = pattern.sub(
                    f'<span class="highlight-suspicious">{phrase}</span>', 
                    highlighted
                )
            except Exception:
                pass
    return highlighted

# ==============================================================================
# WEB PAGE ROUTES
# ==============================================================================

@app.route('/')
def home():
    """Homepage"""
    return render_template('index.html')

@app.route('/scan')
def scan_hub():
    """Scan Center Hub"""
    return render_template('scan.html')

@app.route('/scan/message')
def scan_message_page():
    """Message Scanner Page"""
    return render_template('message_scan.html')

@app.route('/scan/url')
def scan_url_page():
    """URL Scanner Page"""
    return render_template('url_scan.html')

@app.route('/scan/screenshot')
def scan_screenshot_page():
    """Screenshot OCR Scanner Page"""
    return render_template('screenshot_scan.html')

@app.route('/scan/call')
def scan_call_page():
    """Call / Audio Scanner Page"""
    return render_template('call_scan.html')

@app.route('/dashboard')
def dashboard():
    """Security Analytics Dashboard"""
    stats = get_dashboard_analytics()
    return render_template('dashboard.html', stats=stats)

@app.route('/history')
def history_page():
    """Scan History Page with Search, Filtering & Sorting"""
    search = sanitize_input(request.args.get('search', ''))
    filter_risk = sanitize_input(request.args.get('filter_risk', ''))
    sort_by = sanitize_input(request.args.get('sort_by', 'newest'))
    
    scans = get_all_scans(limit=100, search=search, filter_risk=filter_risk, sort_by=sort_by)
    return render_template('history.html', scans=scans, search=search, filter_risk=filter_risk, sort_by=sort_by)

@app.route('/history/<int:scan_id>')
def scan_detail(scan_id):
    """View Detailed Result Page from History"""
    scan = get_scan_by_id(scan_id)
    if not scan:
        flash("Scan record not found.", "error")
        return redirect(url_for('history_page'))

    result = {
        'score': scan['risk_score'],
        'risk_level': scan['risk_level'],
        'scam_type': scan['scam_category'],
        'explanation': scan['explanation'],
        'warning_signs': scan['warning_signs'],
        'recommended_actions': scan['recommended_actions'],
        'suspicious_phrases': scan['suspicious_phrases'],
        'highlighted_text': apply_phrase_highlights(scan['input_summary'], scan['suspicious_phrases'])
    }
    return render_template('result.html', result=result)

@app.route('/quiz')
def quiz_page():
    """Can You Spot The Scam? Interactive Simulator"""
    return render_template('quiz.html')

@app.route('/safety-center')
def safety_center():
    """Educational Safety Center Knowledgebase"""
    articles = get_safety_articles()
    return render_template('safety_center.html', articles=articles)

# ==============================================================================
# REST API ENDPOINTS
# ==============================================================================

@app.route('/api/analyze-message', methods=['POST'])
def api_analyze_message():
    """Analyze Message endpoint"""
    content = sanitize_input(request.form.get('message', ''))
    if not content:
        if request.is_json:
            return jsonify({'error': 'Message content cannot be empty'}), 400
        flash("Please enter message text to analyze.", "error")
        return redirect(url_for('scan_message_page'))

    result = ai_service.analyze_text(content)
    
    save_scan(
        scan_type='message',
        risk_score=result['score'],
        risk_level=result['risk_level'],
        scam_category=result['scam_type'],
        short_result=f"{result['risk_level']} - {result['scam_type']}",
        warning_signs=result['warning_signs'],
        explanation=result['explanation'],
        recommended_actions=result['recommended_actions'],
        suspicious_phrases=result['suspicious_phrases'],
        input_summary=content
    )

    result['highlighted_text'] = apply_phrase_highlights(content, result['suspicious_phrases'])

    if request.headers.get('Accept') == 'application/json' or request.is_json:
        return jsonify(result)

    return render_template('result.html', result=result)

@app.route('/api/analyze-url', methods=['POST'])
def api_analyze_url():
    """Analyze URL endpoint"""
    target_url = sanitize_input(request.form.get('url', ''))
    if not target_url:
        if request.is_json:
            return jsonify({'error': 'URL cannot be empty'}), 400
        flash("Please enter a URL to check.", "error")
        return redirect(url_for('scan_url_page'))

    result = ai_service.analyze_link(target_url)
    
    save_scan(
        scan_type='url',
        risk_score=result['score'],
        risk_level=result['risk_level'],
        scam_category=result['scam_type'],
        short_result=f"{result['risk_level']} - {result['scam_type']}",
        warning_signs=result['warning_signs'],
        explanation=result['explanation'],
        recommended_actions=result['recommended_actions'],
        suspicious_phrases=result['suspicious_phrases'],
        input_summary=target_url
    )

    result['highlighted_text'] = apply_phrase_highlights(target_url, result['suspicious_phrases'])

    if request.is_json:
        return jsonify(result)

    return render_template('result.html', result=result)

@app.route('/api/extract-ocr', methods=['POST'])
def api_extract_ocr():
    """Upload Screenshot & Extract OCR Text Endpoint (In-Memory Processing)"""
    if 'image' not in request.files:
        return jsonify({'success': False, 'error': 'No image file uploaded'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400

    if not allowed_file(file.filename, 'image'):
        return jsonify({'success': False, 'error': 'Invalid file format. Please upload PNG, JPG, or WEBP.'}), 400

    filename = secure_filename(file.filename)
    
    # Process image in-memory via BytesIO to eliminate ephemeral disk dependency
    file_bytes = file.read()
    image_stream = io.BytesIO(file_bytes)
    
    extracted_text = extract_text_from_image(image_stream, filename_hint=filename)

    return jsonify({
        'success': True,
        'extracted_text': extracted_text
    })

@app.route('/api/analyze-screenshot', methods=['POST'])
def api_analyze_screenshot():
    """Analyze Screenshot Extracted Text Endpoint"""
    extracted_text = sanitize_input(request.form.get('extracted_text', ''))
    if not extracted_text:
        flash("No text provided for analysis.", "error")
        return redirect(url_for('scan_screenshot_page'))

    result = ai_service.analyze_text(extracted_text)
    
    save_scan(
        scan_type='screenshot',
        risk_score=result['score'],
        risk_level=result['risk_level'],
        scam_category=result['scam_type'],
        short_result=f"{result['risk_level']} - {result['scam_type']}",
        warning_signs=result['warning_signs'],
        explanation=result['explanation'],
        recommended_actions=result['recommended_actions'],
        suspicious_phrases=result['suspicious_phrases'],
        input_summary=extracted_text
    )

    result['highlighted_text'] = apply_phrase_highlights(extracted_text, result['suspicious_phrases'])

    if request.is_json:
        return jsonify(result)

    return render_template('result.html', result=result)

@app.route('/api/analyze-call', methods=['POST'])
def api_analyze_call():
    """Analyze Call Transcript or Audio File Endpoint"""
    transcript = sanitize_input(request.form.get('transcript', ''))
    
    # Handle Audio File Upload if present (in-memory buffer stream)
    if 'audio_file' in request.files and request.files['audio_file'].filename != '':
        audio_file = request.files['audio_file']
        if allowed_file(audio_file.filename, 'audio'):
            filename = secure_filename(audio_file.filename)
            transcript = transcribe_audio_file(filename)

    if not transcript:
        flash("Please provide a call transcript or audio recording.", "error")
        return redirect(url_for('scan_call_page'))

    result = ai_service.analyze_transcript(transcript)
    
    save_scan(
        scan_type='call',
        risk_score=result['score'],
        risk_level=result['risk_level'],
        scam_category=result['scam_type'],
        short_result=f"{result['risk_level']} - {result['scam_type']}",
        warning_signs=result['warning_signs'],
        explanation=result['explanation'],
        recommended_actions=result['recommended_actions'],
        suspicious_phrases=result['suspicious_phrases'],
        input_summary=transcript
    )

    result['highlighted_text'] = apply_phrase_highlights(transcript, result['suspicious_phrases'])

    if request.is_json:
        return jsonify(result)

    return render_template('result.html', result=result)

@app.route('/api/demo-examples')
def api_demo_examples():
    """Get Demo Examples Endpoint"""
    return jsonify({'examples': get_demo_examples()})

@app.route('/api/quiz/questions')
def api_quiz_questions():
    """Get Quiz Questions Endpoint"""
    return jsonify({'questions': get_quiz_questions()})

@app.route('/api/quiz/submit', methods=['POST'])
def api_quiz_submit():
    """Submit Quiz Results Endpoint"""
    data = request.get_json() or {}
    score = int(data.get('score', 0))
    total = int(data.get('total', 1))
    accuracy = float(data.get('accuracy', 0.0))
    
    new_awareness_score = save_quiz_result(score, total, accuracy)
    return jsonify({'success': True, 'new_awareness_score': new_awareness_score})

@app.route('/api/history')
def api_get_history():
    """Get Scan History API Endpoint"""
    scans = get_all_scans(limit=50)
    return jsonify({'scans': scans})

@app.route('/api/history/<int:scan_id>', methods=['DELETE'])
def api_delete_history(scan_id):
    """Delete Scan Item API Endpoint"""
    success = delete_scan_by_id(scan_id)
    if success:
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Item not found'}), 404

# ==============================================================================
# ERROR HANDLERS
# ==============================================================================

@app.errorhandler(404)
def not_found_error(error):
    return render_template('result.html', result={
        'score': 0,
        'risk_level': 'NEEDS VERIFICATION',
        'scam_type': 'Page Not Found (404)',
        'explanation': 'The requested page or route could not be found on ScamShield.',
        'warning_signs': ['Invalid route URL'],
        'recommended_actions': ['Return to the homepage to access available features.'],
        'suspicious_phrases': [],
        'highlighted_text': '404 - Page Not Found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('result.html', result={
        'score': 0,
        'risk_level': 'NEEDS VERIFICATION',
        'scam_type': 'Internal Server Error (500)',
        'explanation': 'An unexpected server error occurred during processing.',
        'warning_signs': ['Server exception'],
        'recommended_actions': ['Please try submitting your request again or return to the homepage.'],
        'suspicious_phrases': [],
        'highlighted_text': '500 - Internal Server Error'
    }), 500

# Server Entry Point
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug_mode = os.getenv('DEBUG', 'False').lower() == 'true'
    print(f"[ScamShield] Server running on http://127.0.0.1:{port}")
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
