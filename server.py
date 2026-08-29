import os
import sys
import time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, List

# Add path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from nirmaya.core import NirmayaBot
from nirmaya.triage.emergency_protocols import EmergencyProtocols

app = FastAPI(
    title="Nirmaya - AI Health Chatbot API",
    description="Grounded Multilingual RAG Healthcare Assistant (Smart India Hackathon Project)",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

bot = NirmayaBot()

class ChatRequest(BaseModel):
    query: str
    language: Optional[str] = None

class ExportSummaryRequest(BaseModel):
    patient_name: str = "Anonymous Patient"
    query_history: List[dict]

@app.get("/api/health")
def health_check():
    return {"status": "online", "name": "Nirmaya AI Health Chatbot", "version": "1.0.0"}

@app.post("/api/chat")
def handle_chat(req: ChatRequest):
    result = bot.process_query(query=req.query, forced_lang=req.language)
    return {"status": "success", "data": result}

@app.get("/api/emergency-hotlines")
def get_emergency_hotlines():
    return {"hotlines": EmergencyProtocols.EMERGENCY_HOTLINES}

@app.get("/api/conditions")
def list_conditions():
    return {"count": len(bot.vector_store.documents), "conditions": [d["condition"] for d in bot.vector_store.documents]}

@app.post("/api/export-summary", response_class=HTMLResponse)
def export_summary(req: ExportSummaryRequest):
    rows = ""
    for item in req.query_history:
        rows += f"""
        <div style="border-bottom: 1px solid #e2e8f0; padding: 12px 0;">
            <p><strong>Query / Symptoms:</strong> {item.get('query', '')}</p>
            <p><strong>Triage Level:</strong> <span style="background: #f1f5f9; padding: 2px 8px; border-radius: 4px;">{item.get('triage', {}).get('badge', 'N/A')}</span></p>
            <p><strong>Guidance Summary:</strong> {item.get('response', '').replace('\n', '<br>')}</p>
        </div>
        """

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Nirmaya Health Summary — Doctor Consultation Note</title>
        <style>
            body {{ font-family: Arial, sans-serif; padding: 30px; color: #1e293b; line-height: 1.6; max-width: 800px; margin: auto; }}
            .header {{ border-bottom: 2px solid #0284c7; padding-bottom: 15px; margin-bottom: 20px; }}
            .disclaimer {{ background: #fffbeb; border: 1px solid #fef3c7; color: #92400e; padding: 12px; border-radius: 6px; font-size: 12px; margin-top: 30px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1 style="color: #0284c7; margin: 0;">Nirmaya Health Assistant — Pre-Consultation Summary</h1>
            <p style="color: #64748b; font-size: 13px; margin: 5px 0 0 0;">Generated on {time.strftime('%B %d, %Y at %H:%M:%S')} • Patient: {req.patient_name}</p>
        </div>
        <h3>Reported Symptoms & AI Triage Record:</h3>
        {rows}
        <div class="disclaimer">
            <strong>Physician Note:</strong> This summary was prepared using the Nirmaya AI Health Chatbot during patient triage intake. All recommendations are preliminary and subject to full clinical examination by the consulting physician.
        </div>
        <button onclick="window.print()" style="margin-top: 20px; padding: 10px 20px; background: #0284c7; color: white; border: none; border-radius: 6px; cursor: pointer;">Print / Save as PDF</button>
    </body>
    </html>
    """
    return html

# Mount Frontend Static files
frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/css", StaticFiles(directory=os.path.join(frontend_dir, "css")), name="css")
    app.mount("/js", StaticFiles(directory=os.path.join(frontend_dir, "js")), name="js")

    @app.get("/", response_class=HTMLResponse)
    def serve_ui():
        with open(os.path.join(frontend_dir, "index.html"), "r", encoding="utf-8") as f:
            return f.read()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8002)
