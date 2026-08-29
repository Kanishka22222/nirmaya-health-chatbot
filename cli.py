import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from nirmaya.core import NirmayaBot

def run_cli():
    print("=" * 70)
    print("   🌿 NIRMAYA — Grounded AI Health Chatbot (SIH Project)   ")
    print("=" * 70)
    print("Features:")
    print(" • Retrieval-Augmented Generation (RAG) over verified medical protocols")
    print(" • Multilingual symptom support (English, Hindi, Bengali)")
    print(" • Clinical Triage urgency rating (Green: Mild, Yellow: Moderate, Red: Emergency)")
    print(" • Strict medical disclaimers & doctor handoff advice\n")
    print("Type 'exit' to quit.\n")

    bot = NirmayaBot()

    while True:
        try:
            query = input("💬 Enter your symptoms/health query: ").strip()
            if not query:
                continue
            if query.lower() in ["exit", "quit", "bye"]:
                print("👋 Nirmaya: Stay healthy and take care! Goodbye.")
                break

            result = bot.process_query(query)
            triage = result["triage"]
            print(f"\n[TRIAGE]: {triage['badge']}")
            print(f"[ACTION]: {triage['action_advice']}")
            print("-" * 70)
            print(result["response"])
            print("-" * 70)
            print(f"{result['disclaimer']}\n")
        except KeyboardInterrupt:
            print("\n👋 Nirmaya: Shutting down. Take care!")
            break

if __name__ == "__main__":
    run_cli()
