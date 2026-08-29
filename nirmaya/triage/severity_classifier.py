from nirmaya.triage.emergency_protocols import EmergencyProtocols

class SeverityClassifier:
    """Triage Urgency Classifier: Green (Mild), Yellow (Moderate), Red (Emergency)"""

    @classmethod
    def classify(cls, query: str, retrieved_docs: list = None) -> dict:
        # 1. First priority: Check Emergency Protocols
        em_check = EmergencyProtocols.evaluate_emergency(query)
        if em_check["is_emergency"]:
            return {
                "level": "EMERGENCY",
                "badge": "🔴 Emergency (Red Alert)",
                "color": "#ef4444",
                "recommended_timeframe": "Immediate (Within minutes)",
                "action_advice": "Do not wait. Contact an ambulance or go to the nearest emergency ER.",
                "hotlines": em_check["hotlines"]
            }

        # 2. Check if retrieved knowledge base document has a default severity
        if retrieved_docs and len(retrieved_docs) > 0:
            top_doc = retrieved_docs[0]
            default_triage = top_doc.get("triage_default", "MILD")
            if default_triage == "EMERGENCY":
                return {
                    "level": "EMERGENCY",
                    "badge": "🔴 Emergency (Red Alert)",
                    "color": "#ef4444",
                    "recommended_timeframe": "Immediate",
                    "action_advice": "Immediate medical attention strongly indicated.",
                    "hotlines": EmergencyProtocols.EMERGENCY_HOTLINES["India"]
                }
            elif default_triage == "MODERATE":
                return {
                    "level": "MODERATE",
                    "badge": "🟡 Moderate (Consult Doctor)",
                    "color": "#f59e0b",
                    "recommended_timeframe": "Within 24 to 48 Hours",
                    "action_advice": "Consult a registered medical practitioner / primary health center for physical examination."
                }

        # 3. Default to Mild / Home Care
        return {
            "level": "MILD",
            "badge": "🟢 Mild (Home Care & Monitoring)",
            "color": "#10b981",
            "recommended_timeframe": "Self-monitor for 3-5 days",
            "action_advice": "Manage with supportive home care and hydration. Seek medical advice if symptoms worsen."
        }
