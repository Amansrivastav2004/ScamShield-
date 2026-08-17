import re
from urllib.parse import urlparse
from utils.risk_engine import calculate_risk_score

SHORTENER_DOMAINS = {'bit.ly', 'tinyurl.com', 't.co', 'is.gd', 'ow.ly', 'buff.ly', 'goo.gl', 'rb.gy', 'cutt.ly', 'shorturl.at'}
SUSPICIOUS_TLDS = {'.top', '.xyz', '.tk', '.ml', '.ga', '.cf', '.gq', '.zip', '.club', '.online', '.work', '.biz'}
BRAND_KEYWORDS = ['sbi', 'hdfc', 'icici', 'axis', 'paytm', 'gpay', 'phonepe', 'amazon', 'flipkart', 'netflix', 'google', 'apple', 'yono']

def analyze_url(url_string):
    """
    Perform heuristic analysis on target URL.
    Returns structured risk evaluation with disclaimer.
    """
    if not url_string or not url_string.strip():
        return calculate_risk_score([])

    url = url_string.strip()
    if not url.startswith(('http://', 'https://')):
        url_formatted = 'http://' + url
    else:
        url_formatted = url

    indicators = []
    
    try:
        parsed = urlparse(url_formatted)
        hostname = parsed.hostname or ''
        hostname_lower = hostname.lower()
        path_lower = (parsed.path + '?' + parsed.query).lower()
    except Exception:
        hostname_lower = url.lower()
        path_lower = ''

    # 1. IP Address URL (Weight: 35)
    if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', hostname_lower):
        indicators.append({
            'name': 'URL Uses Raw IP Address Instead of Domain Name',
            'weight': 35,
            'phrase': hostname_lower,
            'category': 'Phishing'
        })

    # 2. URL Shortener Service (Weight: 25)
    if any(shortener in hostname_lower for shortener in SHORTENER_DOMAINS):
        indicators.append({
            'name': 'Uses URL Shortener Service (Hides True Destination)',
            'weight': 25,
            'phrase': hostname_lower,
            'category': 'Phishing'
        })

    # 3. Brand Spoofing / Hyphenated Domain Keywords (Weight: 35)
    for brand in BRAND_KEYWORDS:
        if brand in hostname_lower and not hostname_lower.endswith(f'.{brand}.com') and hostname_lower != f'{brand}.com':
            if '-' in hostname_lower or 'verify' in hostname_lower or 'kyc' in hostname_lower or 'login' in hostname_lower or 'update' in hostname_lower:
                indicators.append({
                    'name': f'Lookalike Domain Spoofing Popular Brand ({brand.upper()})',
                    'weight': 35,
                    'phrase': hostname_lower,
                    'category': 'Phishing'
                })
                break

    # 4. Excessive Subdomains (Weight: 20)
    subdomain_parts = hostname_lower.split('.')
    if len(subdomain_parts) >= 4 and not any(shortener in hostname_lower for shortener in SHORTENER_DOMAINS):
        indicators.append({
            'name': 'Excessive Subdomain Levels (> 3 domain parts)',
            'weight': 20,
            'phrase': hostname_lower,
            'category': 'Phishing'
        })

    # 5. Suspicious TLD (Weight: 20)
    if any(hostname_lower.endswith(tld) for tld in SUSPICIOUS_TLDS):
        indicators.append({
            'name': 'Uses High-Risk / Low-Cost Top Level Domain (TLD)',
            'weight': 20,
            'phrase': hostname_lower,
            'category': 'Phishing'
        })

    # 6. Missing HTTPS Encryption (Weight: 15)
    if url_formatted.startswith('http://') and not hostname_lower.startswith('localhost'):
        indicators.append({
            'name': 'Unencrypted HTTP Connection (No SSL/TLS Certificate)',
            'weight': 15,
            'phrase': 'http://',
            'category': 'Phishing'
        })

    # 7. Suspicious Keywords in Path/Query (Weight: 20)
    suspicious_path_terms = ['login', 'verify', 'update', 'kyc', 'secure', 'account', 'banking', 'free-gift', 'claim', 'winner', 'otp']
    found_terms = [term for term in suspicious_path_terms if term in path_lower or term in hostname_lower]
    if found_terms:
        indicators.append({
            'name': f'Contains Phishing Trigger Keywords in URL: ({", ".join(found_terms[:3])})',
            'weight': 20,
            'phrase': found_terms[0],
            'category': 'Phishing'
        })

    # 8. Unusually Long URL or Suspicious Characters (Weight: 15)
    if len(url) > 90 or '@' in url or '//' in url[8:]:
        indicators.append({
            'name': 'Suspicious URL Structure or Obfuscated Parameters',
            'weight': 15,
            'phrase': url[:50] + '...',
            'category': 'Phishing'
        })

    result = calculate_risk_score(indicators)
    result['disclaimer'] = "URL analysis is heuristic unless a verified threat-intelligence service/API is connected."
    return result
