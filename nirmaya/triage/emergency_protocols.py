import re

class EmergencyProtocols:
    """Clinical Emergency Detection and National Hotline Directory"""

    EMERGENCY_HOTLINES = {
        "India": {
            "National_Emergency": "112",
            "Ambulance": "108",
            "Medical_Helpline": "104",
            "Women_Helpline": "1091",
            "Poison_Control": "1800-116-117 (AIIMS New Delhi)"
        },
        "International": {
            "USA_Canada": "911",
            "UK": "999",
            "Europe": "112"
        }
    }

    RED_FLAG_PATTERNS = [
        r'\b(?:chest\s*pain|heart\s*attack|crushing\s*chest|angina)\b',
        r'\b(?:difficulty\s*breathing|cannot\s*breathe|severe\s*shortness\s*of\s*breath|suffocating)\b',
        r'\b(?:stroke|facial\s*droop|arm\s*weakness|slurred\s*speech|paralysis)\b',
        r'\b(?:severe\s*bleeding|hemorrhage|coughing\s*blood|vomiting\s*blood)\b',
        r'\b(?:unconscious|unresponsive|fainted|loss\s*of\s*consciousness|seizure|fits)\b',
        r'\b(?:poison|swallowed\s*chemical|overdose|snake\s*bite)\b',
        r'\b(?:severe\s*burns|electric\s*shock)\b'
    ]

    @classmethod
    def evaluate_emergency(cls, text: str) -> dict:
        q = text.lower()
        matched_flags = []
        for pattern in cls.RED_FLAG_PATTERNS:
            if re.search(pattern, q):
                matched_flags.append(pattern)

        is_emergency = len(matched_flags) > 0
        return {
            "is_emergency": is_emergency,
            "flags_detected": len(matched_flags),
            "emergency_message": (
                "🚨 CRITICAL MEDICAL ALERT: Your query contains red-flag emergency symptoms. "
                "Please CALL EMERGENCY SERVICES (112 / 108 in India, 911 in US) IMMEDIATELY or rush to the nearest emergency department."
            ) if is_emergency else "",
            "hotlines": cls.EMERGENCY_HOTLINES["India"]
        }
