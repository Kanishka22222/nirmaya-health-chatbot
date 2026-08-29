import unittest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from nirmaya.rag.vector_store import MedicalVectorStore
from nirmaya.triage.severity_classifier import SeverityClassifier
from nirmaya.triage.emergency_protocols import EmergencyProtocols
from nirmaya.nlp.multilingual import MultilingualEngine
from nirmaya.core import NirmayaBot

class TestNirmayaChatbot(unittest.TestCase):
    def setUp(self):
        self.bot = NirmayaBot()
        self.store = MedicalVectorStore()

    def test_01_knowledge_base_loading(self):
        self.assertGreater(len(self.store.documents), 0)
        self.assertIn("condition", self.store.documents[0])

    def test_02_vector_search_fever(self):
        results = self.store.search("high fever with shivering and body pain", top_k=2)
        self.assertGreater(len(results), 0)
        top = results[0]
        self.assertIn("Fever", top["condition"])
        self.assertGreater(top["relevance_score"], 0.1)

    def test_03_emergency_protocol_detection(self):
        em = EmergencyProtocols.evaluate_emergency("I have severe crushing chest pain and shortness of breath")
        self.assertTrue(em["is_emergency"])
        self.assertIn("112", em["hotlines"]["National_Emergency"])

    def test_04_triage_classification(self):
        # Emergency test
        triage_red = SeverityClassifier.classify("patient collapsed and has chest pain")
        self.assertEqual(triage_red["level"], "EMERGENCY")

        # Mild test
        triage_green = SeverityClassifier.classify("mild sore throat and runny nose")
        self.assertEqual(triage_green["level"], "MILD")

    def test_05_multilingual_detection(self):
        lang_hi = MultilingualEngine.detect_language("मुझे 2 दिन से बहुत तेज बुखार है")
        self.assertEqual(lang_hi, "hi")

        lang_en = MultilingualEngine.detect_language("I need information on acidity home remedies")
        self.assertEqual(lang_en, "en")

    def test_06_core_rag_pipeline(self):
        output = self.bot.process_query("What are the warning signs and home care for Dengue?")
        self.assertIn("Dengue", output["response"])
        self.assertGreater(len(output["citations"]), 0)
        self.assertIn("Medical Disclaimer", output["disclaimer"])
        self.assertGreater(len(output["follow_up_questions"]), 0)

if __name__ == "__main__":
    unittest.main()
