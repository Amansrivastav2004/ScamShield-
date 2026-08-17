import unittest
import os
import sys
import json

# Add parent folder to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from database.database import init_db, save_scan, get_all_scans, delete_scan_by_id
from utils.risk_engine import calculate_risk_score
from utils.message_analyzer import analyze_message
from utils.url_analyzer import analyze_url
from utils.audio_transcriber import analyze_call_transcript

class ScamShieldTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()
        init_db()

    def test_pages_status_code(self):
        """Test GET status codes for all main pages."""
        pages = ['/', '/scan', '/scan/message', '/scan/url', '/scan/screenshot', '/scan/call', '/dashboard', '/history', '/quiz', '/safety-center']
        for page in pages:
            response = self.client.get(page)
            self.assertEqual(response.status_code, 200, f"Page {page} failed with status {response.status_code}")

    def test_message_analyzer_high_risk(self):
        """Test Message Analyzer detects High Risk KYC Scam."""
        scam_text = "Dear customer, your SBI Bank account will be blocked today due to pending KYC. Update PAN at http://sbi-verify.top or share OTP."
        result = analyze_message(scam_text)
        self.assertGreaterEqual(result['score'], 75)
        self.assertEqual(result['risk_level'], 'HIGH RISK')
        self.assertIn(result['scam_type'], ['KYC Scam', 'Phishing'])
        self.assertIn('Requests Sensitive Credentials (OTP/PIN/Password)', result['warning_signs'])

    def test_message_analyzer_safe(self):
        """Test Message Analyzer classifies genuine notification as Likely Safe."""
        safe_text = "Your Amazon order of Wireless Headphones is out for delivery. Share OTP 4920 upon physical delivery of parcel."
        result = analyze_message(safe_text)
        self.assertLess(result['score'], 50)

    def test_url_analyzer_spoofing(self):
        """Test URL Analyzer detects IP and lookalike bank domains."""
        url = "http://192.168.1.1/sbi-verify-kyc.top"
        result = analyze_url(url)
        self.assertGreaterEqual(result['score'], 50)
        self.assertIn('URL Uses Raw IP Address Instead of Domain Name', result['warning_signs'])

    def test_call_transcript_digital_arrest(self):
        """Test Call Analyzer detects authority impersonation and digital arrest threat."""
        transcript = "This is Officer Sharma from CBI Crime Branch. An illegal narcotics parcel was seized. You are under Digital Arrest. Transfer Rs 50,000 immediately."
        result = analyze_call_transcript(transcript)
        self.assertGreaterEqual(result['score'], 75)
        self.assertEqual(result['risk_level'], 'HIGH RISK')
        self.assertEqual(result['scam_type'], 'Impersonation')

    def test_database_crud(self):
        """Test SQLite save, query, and delete scan."""
        scan_id = save_scan(
            scan_type='message',
            risk_score=90,
            risk_level='HIGH RISK',
            scam_category='KYC Scam',
            short_result='Test Result',
            warning_signs=['Test Sign'],
            explanation='Test Explanation',
            recommended_actions=['Test Action'],
            suspicious_phrases=['Test Phrase'],
            input_summary='Test Summary'
        )
        self.assertIsNotNone(scan_id)
        scans = get_all_scans(limit=10)
        self.assertTrue(any(s['id'] == scan_id for s in scans))
        
        deleted = delete_scan_by_id(scan_id)
        self.assertTrue(deleted)

    def test_api_analyze_message(self):
        """Test API endpoint /api/analyze-message."""
        res = self.client.post('/api/analyze-message', data={'message': 'Urgent: Pay Rs 5000 to unblock your account'}, headers={'Accept': 'application/json'})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('score', data)
        self.assertIn('risk_level', data)

    def test_api_quiz_questions(self):
        """Test API endpoint /api/quiz/questions."""
        res = self.client.get('/api/quiz/questions')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('questions', data)
        self.assertGreater(len(data['questions']), 0)

if __name__ == '__main__':
    unittest.main()
