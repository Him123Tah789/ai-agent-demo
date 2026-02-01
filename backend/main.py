from fastapi import FastAPI, Body, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import traceback

from agent.db import init_db, save_memory, load_memory
from agent.file_reader import read_pdf_to_qa
from agent.document_store import save_document, find_best_answer

app = FastAPI()

# -------------------------------------------------
# CORS
# -------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------
# Init DB
# -------------------------------------------------
init_db()

# -------------------------------------------------
# MULTI DOCUMENT UPLOAD
# -------------------------------------------------
@app.post("/upload-documents")
async def upload_documents(
    files: list[UploadFile] = File(...),
    session_id: str = Form(...)
):
    try:
        for file in files:
            temp_path = f"temp_{file.filename}"

            with open(temp_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            qa_pairs = read_pdf_to_qa(temp_path)
            os.remove(temp_path)

            save_document(session_id, qa_pairs)

        return {
            "status": "success",
            "message": f"{len(files)} document(s) indexed successfully"
        }

    except Exception as e:
        traceback.print_exc()
        return {"status": "error", "message": str(e)}


# -------------------------------------------------
# TEXT QUESTION → DOCUMENT MATCHER
# -------------------------------------------------
@app.post("/process/text")
async def process_text(payload: dict = Body(...)):
    try:
        question = payload.get("input", "").strip()
        agent_type = payload.get("agent_type", "Customer Support")
        session_id = payload.get("session_id")

        if not question or not session_id:
            return {
                "thinking_steps": ["Invalid request"],
                "action": "Rejected",
                "confidence": 0.0,
                "human_needed": True,
                "explanation": "Missing question or session ID",
                "memory": []
            }

        # 🔍 MATCH QUESTION AGAINST DOCUMENTS
        match, score = find_best_answer(session_id, question)

        save_memory(session_id, agent_type, question)

        if not match or score < 0.4:
            return {
                "thinking_steps": [
                    "Read user question",
                    "Searched uploaded documents",
                    "No strong match found"
                ],
                "action": "Escalated to human agent",
                "confidence": 0.0,
                "human_needed": True,
                "explanation": "No relevant answer found in documents",
                "memory": [question]
            }

        return {
            "thinking_steps": [
                "Read user question",
                "Searched uploaded documents",
                "Matched relevant document section"
            ],
            "action": "Answered using uploaded documents",
            "confidence": round(score, 2),
            "human_needed": False,
            "explanation": match["answer"],
            "memory": [match["question"]]
        }

    except Exception as e:
        traceback.print_exc()
        return {
            "thinking_steps": ["Internal error"],
            "action": "Failed",
            "confidence": 0.0,
            "human_needed": True,
            "explanation": str(e),
            "memory": []
        }
