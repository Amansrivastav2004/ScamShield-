"""
ScamShield AI Service Layer Abstraction

Provides a unified interface for current transparent rule-based risk engines
and future AI LLM / Threat Intelligence integrations.
"""

import os
from utils.message_analyzer import analyze_message
from utils.url_analyzer import analyze_url
from utils.audio_transcriber import analyze_call_transcript

class AIServiceAdapter:
    """
    Modular abstraction layer for scam analysis engine.
    Supports switching between 'rule_based' (default) and future 'ai_powered' providers.
    """
    def __init__(self, provider=None):
        self.provider = provider or os.getenv('AI_PROVIDER', 'rule_based')

    def analyze_text(self, content):
        """Analyze message, SMS, WhatsApp, or Email text."""
        if self.provider == 'rule_based':
            result = analyze_message(content)
            result['engine_used'] = 'Transparent Rule-Based Engine v1.0'
            return result
        else:
            # Future AI API Integration point (e.g. OpenAI / Gemini)
            # Falls back gracefully to rule-based engine if API key is not configured.
            result = analyze_message(content)
            result['engine_used'] = 'Transparent Rule-Based Engine (AI Adapter Fallback)'
            return result

    def analyze_link(self, url):
        """Analyze suspicious web URL."""
        if self.provider == 'rule_based':
            result = analyze_url(url)
            result['engine_used'] = 'Heuristic Domain Engine v1.0'
            return result
        else:
            result = analyze_url(url)
            result['engine_used'] = 'Heuristic Domain Engine (AI Adapter Fallback)'
            return result

    def analyze_transcript(self, transcript):
        """Analyze call transcript or audio content."""
        if self.provider == 'rule_based':
            result = analyze_call_transcript(transcript)
            result['engine_used'] = 'Voice Pattern Rule Engine v1.0'
            return result
        else:
            result = analyze_call_transcript(transcript)
            result['engine_used'] = 'Voice Pattern Rule Engine (AI Adapter Fallback)'
            return result

# Global singleton instance
ai_service = AIServiceAdapter()
