import os
import re
from werkzeug.utils import secure_filename

ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'bmp'}
ALLOWED_AUDIO_EXTENSIONS = {'mp3', 'wav', 'm4a', 'ogg'}

def allowed_file(filename, file_type='image'):
    """Validate file extension securely."""
    if not filename or '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    if file_type == 'image':
        return ext in ALLOWED_IMAGE_EXTENSIONS
    elif file_type == 'audio':
        return ext in ALLOWED_AUDIO_EXTENSIONS
    return False

def sanitize_input(text):
    """Sanitize user text input to prevent XSS and formatting issues."""
    if not text:
        return ""
    return text.strip()

def get_demo_examples():
    """
    10 Realistic fictional demo examples for quick testing and demonstration.
    Clearly labeled as fictional/demo data.
    """
    return [
        {
            'id': 'demo_kyc',
            'title': 'Fake Bank KYC Alert (High Risk)',
            'type': 'message',
            'category': 'KYC Scam',
            'content': "Dear Customer, your SBI Bank account ending with 4092 has been BLOCKED today due to incomplete KYC! Immediately verify your PAN & Aadhaar details at http://sbi-bank-verify-kyc.top or call 9876543210 to avoid permanent account deactivation within 24 hours."
        },
        {
            'id': 'demo_upi',
            'title': 'Fake UPI Cashback Collect Request (High Risk)',
            'type': 'message',
            'category': 'UPI Scam',
            'content': "GPay Notification: Congratulations! You have received Rs 2,500 cashback reward from Google Pay Official. Click here to approve collect request and enter your UPI PIN to claim reward directly into your bank account."
        },
        {
            'id': 'demo_job',
            'title': 'Fake WFH Job Offer (High Risk)',
            'type': 'message',
            'category': 'Job Scam',
            'content': "Urgent Hiring! Work from home part-time job. Earn Rs 3,000 to Rs 8,000 daily by simply liking YouTube videos and rating Google places. No experience required. To register, deposit Rs 999 refundable registration fee via PhonePe."
        },
        {
            'id': 'demo_lottery',
            'title': 'Fake KBC Lottery Winner (High Risk)',
            'type': 'message',
            'category': 'Lottery Scam',
            'content': "Dear Sir, Congratulations! Your mobile number won Rs 25,00,000 in KBC All India Lucky Draw 2026. Contact KBC manager Rana Pratap on WhatsApp +91-9876543210. Pay Rs 4,500 government tax fee to receive prize money."
        },
        {
            'id': 'demo_digital_arrest',
            'title': 'Fake Police / Digital Arrest Threat (High Risk)',
            'type': 'call',
            'category': 'Impersonation',
            'content': "This is Inspector Sharma calling from Mumbai Customs Crime Branch. A parcel shipped under your Aadhaar number containing illegal narcotics was seized at international airport. You are under Digital Arrest. Keep your video camera ON, do not tell anyone, and immediately transfer Rs 1,00,000 security deposit to government verification account to avoid arrest."
        },
        {
            'id': 'demo_remote_access',
            'title': 'Fake Electricity Bill Support (High Risk)',
            'type': 'message',
            'category': 'Remote Access Scam',
            'content': "Electricity Alert: Dear consumer, your power supply will be disconnected tonight at 9:30 PM because your last bill of Rs 420 is updated as unpaid. Contact power helpline 9876543210 and download AnyDesk app for screen support."
        },
        {
            'id': 'demo_url_phish',
            'title': 'Suspicious Banking URL (High Risk)',
            'type': 'url',
            'category': 'Phishing',
            'content': "http://192.168.1.1/sbi-verify-login-update.xyz?account=secure"
        },
        {
            'id': 'demo_invest',
            'title': 'Guaranteed Crypto Investment Scheme (High Risk)',
            'type': 'message',
            'category': 'Investment Scam',
            'content': "Join VIP Crypto Signals group! Double your money in 24 hours guaranteed. Invest Rs 5,000 and get Rs 15,000 profit payout tomorrow. 100% risk-free automated AI trading system."
        },
        {
            'id': 'demo_safe_delivery',
            'title': 'Genuine Delivery Notification (Likely Safe)',
            'type': 'message',
            'category': 'Likely Safe Content',
            'content': "Your Amazon order #408-1234567-8910111 containing Wireless Headphones is out for delivery with agent Rajesh. Share OTP 4829 ONLY upon physical delivery of parcel."
        },
        {
            'id': 'demo_safe_bank',
            'title': 'Genuine Bank Transaction Alert (Likely Safe)',
            'type': 'message',
            'category': 'Likely Safe Content',
            'content': "Rs 1,200.00 debited from your A/C **9102 on 17-AUG-26 at Star Supermarket via UPI/Ref 6231904. If not done by you, block card via official mobile app or call 1800-11-2211."
        }
    ]

def get_quiz_questions():
    """
    10+ Realistic fictional scam quiz questions with detailed explanations.
    """
    return [
        {
            'id': 1,
            'difficulty': 'Easy',
            'question': "You receive an SMS: 'Your bank account will be blocked today. Click http://sbi-update-kyc.top to verify your PAN.' What should you do?",
            'options': [
                {'text': "Click the link immediately to prevent account blocking", 'is_correct': False},
                {'text': "Reply to the SMS with your PAN details", 'is_correct': False},
                {'text': "Delete the message and verify via official bank app", 'is_correct': True},
                {'text': "Forward the link to friends to test it", 'is_correct': False}
            ],
            'explanation': "Banks NEVER send unsolicited SMS with external unverified web links asking to update KYC or PAN. Always log in directly to your official bank app."
        },
        {
            'id': 2,
            'difficulty': 'Easy',
            'question': "Someone buying your old sofa online sends a UPI Collect Request for ₹5,000 saying 'Enter your UPI PIN to receive payment'. Is this genuine?",
            'options': [
                {'text': "Yes, entering UPI PIN is required to receive money", 'is_correct': False},
                {'text': "No! Entering your UPI PIN ALWAYS DEDUCTS money from your account", 'is_correct': True},
                {'text': "Yes, if they claim to be an army officer", 'is_correct': False},
                {'text': "Only if they send a QR code first", 'is_correct': False}
            ],
            'explanation': "GOLDEN RULE OF UPI: You NEVER enter your UPI PIN to RECEIVE money. Entering your PIN ALWAYS deducts money from your account!"
        },
        {
            'id': 3,
            'difficulty': 'Medium',
            'question': "A caller claiming to be Customer Care asks you to download 'AnyDesk' or 'QuickSupport' on your phone to resolve a refund. Should you install it?",
            'options': [
                {'text': "Yes, it is a standard support tool", 'is_correct': False},
                {'text': "NO! These are remote-control apps that give fraudsters full control of your phone and OTPs", 'is_correct': True},
                {'text': "Yes, but only if you disable mobile data later", 'is_correct': False},
                {'text': "Yes, if they promise a full refund", 'is_correct': False}
            ],
            'explanation': "Remote access apps allow scammers to view your screen in real time, steal OTPs, and control your banking apps remotely. Never install them on caller requests."
        },
        {
            'id': 4,
            'difficulty': 'Medium',
            'question': "You receive a video call from someone in a police uniform claiming you are under 'Digital Arrest' for an illegal parcel. What is the truth?",
            'options': [
                {'text': "Digital Arrest is a fake scam tactic. Real police never conduct video call arrests or demand money", 'is_correct': True},
                {'text': "You must pay a legal deposit immediately to avoid jail", 'is_correct': False},
                {'text': "You should stay on the video call without telling anyone", 'is_correct': False},
                {'text': "You must share your bank password for investigation", 'is_correct': False}
            ],
            'explanation': "There is NO legal concept called 'Digital Arrest' in law. Real law enforcement agencies NEVER arrest people over Skype/WhatsApp video calls or demand money transfers."
        },
        {
            'id': 5,
            'difficulty': 'Hard',
            'question': "Which of the following web URLs is MOST likely a fraudulent phishing link spoofing ICICI Bank?",
            'options': [
                {'text': "https://www.icicibank.com/personal-banking", 'is_correct': False},
                {'text': "http://icici-bank-verify-kyc.top/login", 'is_correct': True},
                {'text': "https://mobile.icicibank.com", 'is_correct': False},
                {'text': "https://netbanking.icicibank.com", 'is_correct': False}
            ],
            'explanation': "Lookalike domains like 'icici-bank-verify-kyc.top' use hyphens, low-cost TLDs (.top), and unencrypted HTTP to mimic legitimate bank domains."
        },
        {
            'id': 6,
            'difficulty': 'Hard',
            'question': "You get a job offer promising ₹5,000/day for liking YouTube videos, but you must pay a ₹1,000 'security deposit' first. Is this safe?",
            'options': [
                {'text': "Safe, because ₹1,000 is a small fee", 'is_correct': False},
                {'text': "SCAM! Legitimate employers NEVER ask candidate job applicants to pay registration fees", 'is_correct': True},
                {'text': "Safe if they send a formal agreement PDF", 'is_correct': False},
                {'text': "Safe if they pay for the first 3 video likes", 'is_correct': False}
            ],
            'explanation': "Paid task scams bait victims with small payouts initially, then trap them into sending thousands of rupees under the guise of security deposits and tax clearing fees."
        }
    ]

def get_safety_articles():
    """
    Safety Center educational topics and articles.
    """
    return [
        {
            'id': 'otp-safety',
            'category': 'OTP & Credential Safety',
            'title': 'The Golden Rules of OTP & PIN Protection',
            'icon': 'fa-key',
            'summary': 'Learn why sharing your One-Time Password (OTP) is equivalent to handing over your wallet key.',
            'content': """
            ### What is an OTP?
            A One-Time Password (OTP) is a second layer of security designed to confirm your identity during financial transactions, password resets, or app logins.

            ### Golden Safeguards:
            1. **NEVER share OTPs over the phone**: Bank managers, customer care reps, police officers, and delivery agents will NEVER ask for your OTP.
            2. **Read the OTP message carefully**: Before entering an OTP, check the merchant name and amount mentioned in the SMS body.
            3. **UPI PIN is ONLY for sending money**: You never enter a UPI PIN to receive money or cashback.
            4. **Beware of call forwarding codes**: Never dial codes like `*21*<number>#` requested by strangers; this forwards your incoming calls and voice OTPs to scammers.
            """
        },
        {
            'id': 'upi-safety',
            'category': 'UPI & Digital Payment Safety',
            'title': 'How to Avoid UPI & QR Code Scams',
            'icon': 'fa-qrcode',
            'summary': 'Understand collect request traps, fake buyer QR codes on OLX/Marketplace, and refund scams.',
            'content': """
            ### Common UPI Scam Tactics:
            - **Fake Buyer QR Code**: Scammers send a QR code claiming "Scan this QR code to receive payment for your item." Scanning a QR code ALWAYS deducts money from your account!
            - **Collect Request Fraud**: Scammers send a ₹10,000 collect request with a note saying "Cashback Approved". Approving it transfers your money to them.

            ### How to Stay Safe:
            - Remember: **PIN is for paying, NOT for receiving.**
            - Check beneficiary name on the UPI confirmation screen before pressing submit.
            - Immediately report fraudulent UPI transactions to your bank and helpline 1930 within the 'Golden Hour'.
            """
        },
        {
            'id': 'phishing-awareness',
            'category': 'Phishing & Fake Links',
            'title': 'Spotting Phishing Links & Fake Websites',
            'icon': 'fa-link',
            'summary': 'How to identify fake bank portals, lookalike domains, and suspicious link shorteners.',
            'content': """
            ### Anatomy of a Phishing Link:
            Phishing links try to mimic trusted brands using tricks like:
            - Hyphenated domain names: `sbi-kyc-update.com` instead of `sbi.co.in`
            - Cheap Top-Level Domains: `.top`, `.xyz`, `.club`, `.work`
            - Raw IP addresses: `http://192.168.1.1/login`
            - URL Shorteners: `bit.ly/3xYz1` that hide the actual destination URL

            ### Actionable Checklist:
            - Always type official website addresses directly into your browser address bar.
            - Look for the padlock symbol (HTTPS) in your browser.
            """
        },
        {
            'id': 'digital-arrest',
            'category': 'Police & Authority Impersonation',
            'title': 'Understanding Fake Police & Digital Arrest Scams',
            'icon': 'fa-user-shield',
            'summary': 'What is a "Digital Arrest" scam and how to react if an official threatens you on video call.',
            'content': """
            ### What is a "Digital Arrest" Scam?
            Fraudsters call pretending to be from Customs, CBI, Crime Branch, or TRAI. They claim an illegal parcel containing drugs, fake passports, or SIM cards has been seized in your name. They compel victims to stay on video calls ("Digital Arrest") for hours while demanding extortion money.

            ### The Truth:
            - **No police force conducts arrests via video call.**
            - **No government agency demands money transfer to "clear your name".**
            - If you receive such a call, disconnect immediately and report the number at `cybercrime.gov.in` or dial 1930.
            """
        },
        {
            'id': 'job-scams',
            'category': 'Fake Job & Task Schemes',
            'title': 'Spotting Fake Work-From-Home & YouTube Like Jobs',
            'icon': 'fa-briefcase',
            'summary': 'Why paying money to get a job is always a scam.',
            'content': """
            ### How Task Scams Work:
            1. You get a WhatsApp message offering ₹3,000/day for liking YouTube videos or reviewing hotels.
            2. They pay ₹200 initially to build trust.
            3. They invite you to a Telegram group and ask you to invest ₹5,000 in "prepaid crypto tasks" for guaranteed 50% returns.
            4. Once you deposit larger sums, they block your withdrawals.

            ### Rule to Remember:
            Legitimate companies pay YOU for work. If a job requires you to pay upfront fees, it is 100% a scam.
            """
        },
        {
            'id': 'remote-access-safety',
            'category': 'Remote Access Software',
            'title': 'Why Installing AnyDesk on Stranger Request is Dangerous',
            'icon': 'fa-desktop',
            'summary': 'Learn how remote screen sharing apps give fraudsters complete control over your smartphone.',
            'content': """
            ### What are Remote Access Apps?
            Apps like AnyDesk, TeamViewer, QuickSupport, and RustDesk are legitimate software used by IT professionals to manage computers remotely.

            ### How Scammers Abuse Them:
            Scammers pose as bank customer support and instruct victims to install these apps to "fix a pending transaction". Once you share the 9-digit remote code, the scammer can see your screen, watch you enter passwords, and capture OTPs in real time.

            ### Defense Strategy:
            Never install or share connection codes for remote screen sharing apps with anyone who calls you unsolicited.
            """
        }
    ]
