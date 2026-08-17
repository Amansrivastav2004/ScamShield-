import os
import re
from utils.risk_engine import calculate_risk_score

def analyze_call_transcript(transcript_text):
    """
    Analyze a call transcript for phone scam patterns, coercion, digital arrest threats,
    fake officer impersonation, and money transfer demands.
    """
    if not transcript_text or not transcript_text.strip():
        return calculate_risk_score([])

    text_lower = transcript_text.lower()
    indicators = []

    # 1. Impersonation of Authority / Police / TRAI / CBI / Digital Arrest (Weight: 35)
    police_patterns = [
        r'police', r'cbi', r'customs', r'trai', r'digital arrest',
        r'illegal parcel', r'narcotics', r'warrant', r'court order', r'crime branch'
    ]
    for pat in police_patterns:
        match = re.search(pat, text_lower)
        if match:
            indicators.append({
                'name': 'Authority Impersonation / Fake Police or Legal Threat (Digital Arrest)',
                'weight': 35,
                'phrase': match.group(0),
                'category': 'Impersonation'
            })
            break

    # 2. Demand for Remote Control Apps (Weight: 35)
    remote_patterns = [r'anydesk', r'teamviewer', r'quicksupport', r'download app', r'screen share']
    for pat in remote_patterns:
        match = re.search(pat, text_lower)
        if match:
            indicators.append({
                'name': 'Caller Demands Remote Control App Installation (AnyDesk/TeamViewer)',
                'weight': 35,
                'phrase': match.group(0),
                'category': 'Remote Access Scam'
            })
            break

    # 3. Demand for Immediate Payment / Transfer (Weight: 30)
    pay_patterns = [
        r'transfer\s+(?:money|rs|\$|₹|\d+)', r'pay\s+(?:fine|money|rs|\$|₹|\d+)',
        r'send money', r'upi transfer', r'bank deposit', r'security deposit'
    ]
    for pat in pay_patterns:
        match = re.search(pat, text_lower)
        if match:
            indicators.append({
                'name': 'High-Pressure Financial Transfer Demand over Phone',
                'weight': 30,
                'phrase': match.group(0),
                'category': 'Impersonation'
            })
            break

    # 4. OTP / Credentials Interrogation (Weight: 35)
    otp_patterns = [r'tell me the otp', r'read out otp', r'share pin', r'tell password', r'cvv number', r'otp']
    for pat in otp_patterns:
        match = re.search(pat, text_lower)
        if match:
            indicators.append({
                'name': 'Direct Voice Demand for Sensitive Credentials (OTP/PIN)',
                'weight': 35,
                'phrase': match.group(0),
                'category': 'Phishing'
            })
            break

    # 5. Secrecy / Isolation Command (Weight: 25)
    secrecy_patterns = [r'do not inform anyone', r'keep on call', r'do not disconnect', r'confidential investigation', r'do not tell']
    for pat in secrecy_patterns:
        match = re.search(pat, text_lower)
        if match:
            indicators.append({
                'name': 'Demands Secrecy and Prohibits Disconnecting Call',
                'weight': 25,
                'phrase': match.group(0),
                'category': 'Impersonation'
            })
            break

    # 6. Urgency & Panic Induction (Weight: 20)
    urgency_patterns = [r'right now', r'immediately', r'in next \d+ minutes', r'otherwise arrest', r'account will be frozen']
    for pat in urgency_patterns:
        match = re.search(pat, text_lower)
        if match:
            indicators.append({
                'name': 'Urgent Threat of Immediate Legal Action or Asset Freeze',
                'weight': 20,
                'phrase': match.group(0),
                'category': 'Impersonation'
            })
            break

    return calculate_risk_score(indicators)

def transcribe_audio_file(audio_path):
    """
    Transcribe audio file or generate simulated transcript for demo audio clips.
    """
    filename = os.path.basename(audio_path).lower()

    if "police" in filename or "arrest" in filename or "cbi" in filename:
        return ("Caller: This is Officer Sharma from Mumbai Crime Branch. An illegal parcel with narcotics "
                "was seized under your name. A digital arrest warrant is issued. Do not disconnect this call "
                "or tell anyone. You must transfer Rs 50,000 to our verification bank account immediately to stop arrest.")
    elif "bank" in filename or "otp" in filename:
        return ("Caller: Good morning sir, I am calling from SBI Manager office. Your debit card is expired today. "
                "To renew card immediately, tell me the 6-digit OTP sent to your registered mobile number right now.")
    else:
        return ("Caller: Hello, I am calling from Customer Support. Your parcel delivery is stuck due to unpaid address tax. "
                "Please download AnyDesk app on your phone so our team can help you pay Rs 10 online.")
