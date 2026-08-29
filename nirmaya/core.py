import time
from typing import Dict, Any, List
from nirmaya.rag.vector_store import MedicalVectorStore
from nirmaya.triage.severity_classifier import SeverityClassifier
from nirmaya.nlp.multilingual import MultilingualEngine

class NirmayaBot:
    """Core RAG Health Chatbot Orchestrator"""

    def __init__(self):
        self.vector_store = MedicalVectorStore()

    def process_query(self, query: str, forced_lang: str = None) -> Dict[str, Any]:
        start_t = time.time()
        
        # 1. Language Detection
        lang = forced_lang if forced_lang else MultilingualEngine.detect_language(query)
        headers = MultilingualEngine.SECTION_HEADERS.get(lang, MultilingualEngine.SECTION_HEADERS["en"])
        disclaimer = MultilingualEngine.DISCLAIMERS.get(lang, MultilingualEngine.DISCLAIMERS["en"])

        # 2. RAG Knowledge Retrieval
        retrieved_docs = self.vector_store.search(query, top_k=2)

        # 3. Triage & Severity Classification
        triage_info = SeverityClassifier.classify(query, retrieved_docs)

        # 4. Construct Grounded Response
        if not retrieved_docs:
            if lang == "hi":
                response_text = (
                    "Aapke dwara bataye gaye lakshan hamare prathmik medical index mein seedhe match nahi huye. "
                    "Kripya adhik vivaran dein (jaise kitne dino se dikkat hai, bukhar ya koi anya takleef). "
                    "Yadi sthiti gambhir hai toh kripya turant nikat-tam doctor ya clinic se sampark karein."
                )
            else:
                response_text = (
                    "I could not find an exact match for these specific symptoms in my verified clinical database. "
                    "Please provide more context (such as symptom duration, severity, or associated discomfort). "
                    "If you are feeling unwell, we recommend consulting a primary healthcare provider."
                )
            citations = []
            follow_ups = ["How many days have you had these symptoms?", "Are you experiencing any fever or acute pain?"]
        else:
            primary_doc = retrieved_docs[0]
            citations = [doc["source"] for doc in retrieved_docs]
            
            # Formulate structured grounded answer
            care_items = "\n".join([f"  • {item}" for item in primary_doc.get("home_care", [])])
            red_flag_items = "\n".join([f"  • {item}" for item in primary_doc.get("red_flags", [])])

            response_text = (
                f"### {headers['assessment']}: **{primary_doc['condition']}**\n\n"
                f"{primary_doc['summary']}\n\n"
                f"#### {headers['home_care']}:\n{care_items}\n\n"
                f"#### {headers['red_flags']}:\n{red_flag_items}\n\n"
                f"**{headers['sources']}**: {', '.join(citations)}"
            )

            follow_ups = [
                f"How long have you noticed these symptoms of {primary_doc['condition'].split('(')[0].strip()}?",
                "Are you currently taking any prescribed medications?",
                "Would you like an export summary note for your doctor visit?"
            ]

        latency_ms = round((time.time() - start_t) * 1000, 2)

        return {
            "query": query,
            "language": lang,
            "triage": triage_info,
            "response": response_text,
            "disclaimer": disclaimer,
            "citations": citations,
            "follow_up_questions": follow_ups,
            "retrieved_count": len(retrieved_docs),
            "latency_ms": latency_ms,
            "timestamp": time.strftime("%H:%M:%S")
        }
