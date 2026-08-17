import re
from utils.risk_engine import calculate_risk_score

def analyze_message(text):
    """
    Analyze SMS, WhatsApp, or Email content for scam patterns and warning indicators.
    Returns calculated risk report.
    """
    if not text or not text.strip():
        return calculate_risk_score([])

    indicators = []
    text_lower = text.lower()

    # 1. Fake KYC / Account Suspension Threat (Weight: 35, Category: KYC Scam)
    kyc_patterns = [
        r'\bkyc\b', r'account.*block', r'account.*suspend', r'deactivate', r'pan card.*link',
        r'electricity.*disconnect', r'sim.*deactivate', r'bank.*block'
    ]
    for pat in kyc_patterns:
        match = re.search(pat, text_lower)
        if match:
            indicators.append({
                'name': 'Urgent Threat of Account Suspension / Fake KYC Warning',
                'weight': 35,
                'phrase': match.group(0),
                'category': 'KYC Scam'
            })
            break

    # 2. OTP / Sensitive Info Request (Weight: 35, Category: Phishing)
    otp_patterns = [
        r'\botp\b', r'\bpin\b', r'\bpassword\b', r'\bcvv\b', r'verification code',
        r'share.*otp', r'tell.*otp', r'send.*pin', r'enter.*pin'
    ]
    for pat in otp_patterns:
        match = re.search(pat, text_lower)
        if match:
            indicators.append({
                'name': 'Requests Sensitive Credentials (OTP/PIN/Password)',
                'weight': 35,
                'phrase': match.group(0),
                'category': 'Phishing'
            })
            break

    # 3. Payment Request / Transfer Pressure (Weight: 30, Category: UPI Scam)
    payment_patterns = [
        r'pay\s+(?:rs|\$|₹)?', r'transfer\s+(?:rs|\$|₹|money)', r'send\s+(?:rs|\$|₹|money)',
        r'upi\s+pin', r'deposit', r'registration\s+fee', r'processing\s+fee',
        r'security\s+deposit', r'paytm', r'phonepe', r'gpay'
    ]
    for pat in payment_patterns:
        match = re.search(pat, text_lower)
        if match:
            indicators.append({
                'name': 'Direct Payment or Money Transfer Demand',
                'weight': 30,
                'phrase': match.group(0),
                'category': 'UPI Scam'
            })
            break

    # 4. Job Offer requiring payment / task scam (Weight: 30, Category: Job Scam)
    job_patterns = [
        r'work from home', r'part time job', r'daily income', r'earn \d+ per day',
        r'like youtube video', r'telegram job', r'registration fee for job'
    ]
    for pat in job_patterns:
        match = re.search(pat, text_lower)
        if match:
            indicators.append({
                'name': 'Suspicious Job Offer / Paid Task Scheme',
                'weight': 30,
                'phrase': match.group(0),
                'category': 'Job Scam'
            })
            break

    # 5. Remote Access Application Request (Weight: 35, Category: Remote Access Scam)
    remote_patterns = [r'anydesk', r'teamviewer', r'quicksupport', r'rustdesk', r'screen share']
    for pat in remote_patterns:
        match = re.search(pat, text_lower)
        if match:
            indicators.append({
                'name': 'Demands Installation of Screen-Sharing / Remote Access Software',
                'weight': 35,
                'phrase': match.group(0),
                'category': 'Remote Access Scam'
            })
            break

    # 6. Unexpected Reward / Lottery Claim (Weight: 30, Category: Lottery Scam)
    lottery_patterns = [
        r'congratulations', r'won\s+(?:rs|\$|₹|\d)', r'lottery winner', r'lucky draw',
        r'claim prize', r'gift card', r'cashback of'
    ]
    for pat in lottery_patterns:
        match = re.search(pat, text_lower)
        if match:
            indicators.append({
                'name': 'Unrealistic Reward / Fake Prize Claim',
                'weight': 30,
                'phrase': match.group(0),
                'category': 'Lottery Scam'
            })
            break

    # 7. Fake Customer Support / Unofficial Helpline (Weight: 25, Category: Fake Customer Care)
    cust_patterns = [r'customer care', r'helpline number', r'contact support', r'call now']
    if any(re.search(pat, text_lower) for pat in cust_patterns) and re.search(r'\+?\d{10,12}', text):
        indicators.append({
            'name': 'Unverified Mobile Number as Official Support Helpline',
            'weight': 25,
            'phrase': 'Customer care mobile number',
            'category': 'Fake Customer Care'
        })

    # 8. Urgency & High Pressure Tactics (Weight: 20, Category: Phishing)
    urgency_patterns = [
        r'immediately', r'within 24 hours', r'today itself', r'urgent action', r'last chance',
        r'strictly required'
    ]
    for pat in urgency_patterns:
        match = re.search(pat, text_lower)
        if match:
            indicators.append({
                'name': 'High-Pressure Urgency Tactics',
                'weight': 20,
                'phrase': match.group(0),
                'category': 'Phishing'
            })
            break

    # 9. Embedded Suspicious URLs or APK links (Weight: 25, Category: Phishing)
    url_match = re.search(r'https?://[^\s]+|www\.[^\s]+|\b\w+\.(?:bit\.ly|tinyurl|top|xyz|cc|app|apk)\b', text_lower)
    if url_match:
        indicators.append({
            'name': 'Contains External or Shortened Web Link',
            'weight': 25,
            'phrase': url_match.group(0),
            'category': 'Phishing'
        })

    # 10. Guaranteed Returns / Investment Scam (Weight: 30, Category: Investment Scam)
    invest_patterns = [r'guaranteed profit', r'double your money', r'crypto investment', r'trading signals']
    for pat in invest_patterns:
        match = re.search(pat, text_lower)
        if match:
            indicators.append({
                'name': 'Unrealistic Investment Profit Promise',
                'weight': 30,
                'phrase': match.group(0),
                'category': 'Investment Scam'
            })
            break

    return calculate_risk_score(indicators)
