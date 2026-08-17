"""
ScamShield Risk Engine
Transparent, rule-based risk evaluation system for cyber threats.
Maps detected indicators to a transparent risk score (0-100) and risk category.
"""

def calculate_risk_score(indicators):
    """
    Calculate risk score from list of detected indicator objects.
    Each indicator: {'name': str, 'weight': int, 'phrase': str, 'category': str}
    """
    total_score = 0
    warning_signs = []
    suspicious_phrases = []
    categories = {}

    for ind in indicators:
        weight = ind.get('weight', 10)
        total_score += weight
        
        desc = ind.get('name', 'Suspicious pattern detected')
        if desc not in warning_signs:
            warning_signs.append(desc)
            
        phrase = ind.get('phrase')
        if phrase and phrase not in suspicious_phrases:
            suspicious_phrases.append(phrase)
            
        cat = ind.get('category', 'Other')
        categories[cat] = categories.get(cat, 0) + weight

    # Cap score at 100 max
    final_score = min(100, total_score)

    # Determine Risk Level
    if final_score >= 75:
        risk_level = "HIGH RISK"
    elif final_score >= 50:
        risk_level = "SUSPICIOUS"
    elif final_score >= 25:
        risk_level = "NEEDS VERIFICATION"
    else:
        risk_level = "LIKELY SAFE"

    # Select primary scam category
    if categories:
        scam_type = max(categories, key=categories.get)
    else:
        scam_type = "Likely Safe Content" if final_score < 25 else "Other"

    # Build contextual explanation
    explanation = build_explanation(risk_level, scam_type, final_score, warning_signs)
    
    # Build contextual recommended actions
    recommended_actions = build_recommended_actions(risk_level, scam_type, warning_signs)

    return {
        'score': final_score,
        'risk_level': risk_level,
        'scam_type': scam_type,
        'warning_signs': warning_signs,
        'explanation': explanation,
        'recommended_actions': recommended_actions,
        'suspicious_phrases': suspicious_phrases,
        'is_definitive': False
    }

def build_explanation(risk_level, scam_type, score, warning_signs):
    """Generate clear, human-understandable risk explanations."""
    if risk_level == "HIGH RISK":
        base = f"This content scored {score}/100 and exhibits critical characteristics commonly seen in {scam_type}s. "
        if warning_signs:
            base += f"Key red flags include: {', '.join(warning_signs[:3]).lower()}."
        else:
            base += "Multiple high-risk indicators were detected."
        return base
    elif risk_level == "SUSPICIOUS":
        base = f"This content scored {score}/100 and shows several suspicious indicators associated with {scam_type}. "
        base += "Exercise extreme caution and do not interact directly with links or instructions."
        return base
    elif risk_level == "NEEDS VERIFICATION":
        base = f"This content scored {score}/100. While no definitive malicious patterns were confirmed, "
        base += "it contains elements (such as links or requests) that require manual verification through official channels."
        return base
    else:
        return (f"This content scored {score}/100. No major scam patterns, sensitive information requests, "
                "or urgent payment threats were detected. However, always remain vigilant.")

def build_recommended_actions(risk_level, scam_type, warning_signs):
    """Generate actionable safety recommendations tailored to the scam type."""
    actions = []
    
    # Category-specific guidance
    if "KYC" in scam_type:
        actions.extend([
            "Do not click any link in unsolicited SMS or WhatsApp messages claiming your account will be blocked.",
            "Verify your account status by logging into the official bank or service website directly.",
            "Remember: Banks and official agencies NEVER update KYC via WhatsApp or external forms."
        ])
    elif "UPI" in scam_type or "Banking" in scam_type:
        actions.extend([
            "Do not transfer money or enter your UPI PIN to RECEIVE funds. Entering your PIN ALWAYS deducts money.",
            "Never approve unexpected UPI collect requests from unknown callers or buyers.",
            "Report fraudulent UPI IDs immediately on the Cyber Crime portal (1930 in India)."
        ])
    elif "Job" in scam_type:
        actions.extend([
            "Legitimate employers NEVER ask candidate job applicants to pay registration, interview, or security fees.",
            "Do not perform online tasks (like liking videos or reviewing places) in exchange for promised daily returns.",
            "Verify company job postings on official career portals like LinkedIn or corporate websites."
        ])
    elif "Remote Access" in scam_type:
        actions.extend([
            "NEVER download remote control apps like AnyDesk, TeamViewer, or QuickSupport on request of an unknown caller.",
            "These apps allow fraudsters to view your phone screen, capture OTPs, and control your banking apps.",
            "If already installed, immediately uninstall the app and turn off Wi-Fi/Mobile Data."
        ])
    elif "Lottery" in scam_type or "Investment" in scam_type:
        actions.extend([
            "Be skeptical of unexpected prizes, lottery winnings, or guaranteed high-return investment schemes.",
            "If you didn't enter a contest, you cannot win a prize. Demands for 'processing fees' or 'tax payment' are fraudulent."
        ])
    elif "Customer Care" in scam_type:
        actions.extend([
            "Do not search for customer service phone numbers on Google Maps or unverified search results.",
            "Always source helpline numbers directly from the back of your credit/debit card or official app."
        ])
    else:
        actions.extend([
            "Do not share OTPs, passwords, PINs, or sensitive identity documents with anyone.",
            "Do not click links from unknown senders or download unexpected email attachments.",
            "If in doubt, contact the official organization using a independently verified contact number."
        ])

    # General critical safeguards for high risk
    if risk_level in ["HIGH RISK", "SUSPICIOUS"]:
        actions.insert(0, "🚨 STOP: Do not transfer money, share OTPs/PINs, or click any links contained in this content.")
        if "If money has already been transferred" not in actions:
            actions.append("If money has been transferred, immediately contact your bank's fraud reporting line and file a report at cybercrime.gov.in (or local helpline).")

    return actions
