/* ScamShield Multilingual Translation System */

const translations = {
    en: {
        tagline: "Don't Trust It. Check It.",
        hero_subtitle: "Scan suspicious messages, links, screenshots, and call transcripts before they put your money or personal information at risk.",
        start_scan: "Start Free Scan",
        how_it_works: "How ScamShield Works",
        check_msg: "Check Message",
        check_url: "Check URL",
        scan_screenshot: "Scan Screenshot",
        check_call: "Check Call",
        nav_home: "Home",
        nav_scan: "Scan",
        nav_dashboard: "Dashboard",
        nav_history: "History",
        nav_quiz: "Quiz",
        nav_safety: "Safety Center",
        disclaimer_notice: "Results are transparent risk assessments, not 100% fraud guarantees.",
        what_next: "What Should I Do Now?",
        analyze_now: "Analyze Risk Now",
        clear_input: "Clear Input",
        load_demo: "Load Demo Example"
    },
    hi: {
        tagline: "भरोसा न करें। जाँच करें।",
        hero_subtitle: "संदिग्ध मैसेज, लिंक, स्क्रीनशॉट और कॉल ट्रांसक्रिप्ट की जांच करें, इससे पहले कि आपका पैसा या व्यक्तिगत जानकारी जोखिम में पड़े।",
        start_scan: "मुफ़्त स्कैन शुरू करें",
        how_it_works: "स्कैमशील्ड कैसे काम करता है",
        check_msg: "मैसेज जांचें",
        check_url: "URL जांचें",
        scan_screenshot: "स्क्रीनशॉट स्कैन करें",
        check_call: "कॉल जांचें",
        nav_home: "होम",
        nav_scan: "स्कैन",
        nav_dashboard: "डैशबोर्ड",
        nav_history: "इतिहास",
        nav_quiz: "क्विज़",
        nav_safety: "सुरक्षा केंद्र",
        disclaimer_notice: "परिणाम पारदर्शी जोखिम मूल्यांकन हैं, 100% धोखाधड़ी की गारंटी नहीं।",
        what_next: "अब मुझे क्या करना चाहिए?",
        analyze_now: "जोखिम विश्लेषण करें",
        clear_input: "साफ़ करें",
        load_demo: "डेमो उदाहरण लोड करें"
    },
    hinglish: {
        tagline: "Don't Trust It. Check It.",
        hero_subtitle: "Suspicious messages, links, screenshots aur call transcripts check karo before money ya personal info risk me pade.",
        start_scan: "Start Free Scan",
        how_it_works: "ScamShield Kaise Kaam Karta Hai",
        check_msg: "Check Message",
        check_url: "Check URL",
        scan_screenshot: "Scan Screenshot",
        check_call: "Check Call",
        nav_home: "Home",
        nav_scan: "Scan",
        nav_dashboard: "Dashboard",
        nav_history: "History",
        nav_quiz: "Quiz",
        nav_safety: "Safety Center",
        disclaimer_notice: "Results transparent risk assessments hain, 100% fraud decision nahi.",
        what_next: "Ab Mujhe Kya Karna Chahiye?",
        analyze_now: "Analyze Risk Now",
        clear_input: "Clear Text",
        load_demo: "Load Demo Example"
    }
};

let currentLanguage = localStorage.getItem('scamshield_lang') || 'en';

function setLanguage(lang) {
    if (!translations[lang]) return;
    currentLanguage = lang;
    localStorage.setItem('scamshield_lang', lang);
    
    // Update active dropdown label
    const labelMap = { en: '🇬🇧 EN', hi: '🇮🇳 हिंदी', hinglish: '🇮🇳 Hinglish' };
    const langBtnText = document.getElementById('currentLangText');
    if (langBtnText) {
        langBtnText.textContent = labelMap[lang] || '🇬🇧 EN';
    }

    // Apply translations to DOM elements with data-i18n attribute
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (translations[lang][key]) {
            el.textContent = translations[lang][key];
        }
    });
}

document.addEventListener('DOMContentLoaded', () => {
    setLanguage(currentLanguage);
});
