import re

class MultilingualEngine:
    """Multilingual Support for English, Hindi (हिंदी), and Bengali (বাংলা)"""

    DISCLAIMERS = {
        "en": "⚠️ Medical Disclaimer: Nirmaya is an AI assistant providing preliminary educational guidance based on verified medical protocols. It does not replace professional medical diagnosis or treatment from a licensed physician.",
        "hi": "⚠️ चिकित्सा अस्वीकरण: निरमाया एक एआई सहायक है जो केवल प्राथमिक मार्गदर्शन प्रदान करता है। यह किसी योग्य चिकित्सक के परामर्श या निदान का विकल्प नहीं है।",
        "bn": "⚠️ চিকিৎসা দাবিত্যাগ: নিরময়া একটি এআই সহকারী যা শুধুমাত্র প্রাথমিক দিকনির্দেশনা প্রদান করে। এটি একজন যোগ্য চিকিৎসকের পরামর্শের বিকল্প নয়।"
    }

    SECTION_HEADERS = {
        "en": {
            "assessment": "🩺 Clinical Overview",
            "home_care": "🌿 Supportive Home Care & Safe Measures",
            "red_flags": "🚨 When to See a Doctor Immediately (Red Flags)",
            "sources": "📚 Verified Grounded Sources"
        },
        "hi": {
            "assessment": "🩺 प्राथमिक स्वास्थ्य विवरण (Clinical Overview)",
            "home_care": "🌿 प्राथमिक घरेलू देखभाल और सावधानियां",
            "red_flags": "🚨 तुरंत डॉक्टर से कब मिलें (चेतावनी संकेत)",
            "sources": "📚 प्रमाणित चिकित्सा स्रोत (Verified Sources)"
        },
        "bn": {
            "assessment": "🩺 প্রাথমিক স্বাস্থ্য সারসংক্ষেপ",
            "home_care": "🌿 ঘরোয়া যত্ন ও প্রাথমিক সতর্কতা",
            "red_flags": "🚨 কখন অবিলম্বে ডাক্তারের কাছে যাবেন",
            "sources": "📚 যাচাইকৃত চিকিৎসা সূত্র"
        }
    }

    @classmethod
    def detect_language(cls, text: str) -> str:
        # Check Devanagari range
        if re.search(r'[\u0900-\u097F]', text):
            return "hi"
        # Check Bengali range
        if re.search(r'[\u0980-\u09FF]', text):
            return "bn"
        
        # Check Hinglish keywords
        hi_words = ["bukhar", "khansi", "sir dard", "pet dard", "dast", "ulti", "kya kare", "ilaj", "jalan"]
        q_lower = text.lower()
        if any(w in q_lower for w in hi_words):
            return "hi"

        return "en"
