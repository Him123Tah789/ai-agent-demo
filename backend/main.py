from fastapi import FastAPI, Body, UploadFile, File, Form
from agent.brain import think_and_plan
from agent.file_reader import read_pdf
from agent.db import init_db, save_memory, load_memory
import shutil
import os

app = FastAPI()

# -------------------------------------------------
# Initialize database on startup
# -------------------------------------------------
init_db()

# -------------------------------------------------
# TEXT INPUT ENDPOINT (JSON ONLY)
# -------------------------------------------------
@app.post("/process/text")
async def process_text(payload: dict = Body(...)):
    user_input = payload.get("input", "")
    agent_type = payload.get("agent_type", "Customer Support")
    session_id = payload.get("session_id")

    if not session_id:
        return {
            "thinking_steps": ["Missing session ID"],
            "action": "Request rejected",
            "confidence": 0.0,
            "human_needed": True,
            "explanation": "Session ID is required for memory tracking.",
            "memory": []
        }

    if not user_input.strip():
        return {
            "thinking_steps": ["No input provided"],
            "action": "No action taken",
            "confidence": 0.0,
            "human_needed": True,
            "explanation": "No input was provided to the agent.",
            "memory": []
        }

    # 🧠 Run agent brain WITH memory
    result = think_and_plan(
        user_input=user_input,
        agent_type=agent_type,
        session_id=session_id
    )

    # 💾 Save memory
    save_memory(session_id, agent_type, user_input)

    # 📥 Load memory to return to frontend
    memory_rows = load_memory(session_id)
    memory_messages = [msg for _, msg in memory_rows]

    # ✅ Attach memory
    result["memory"] = memory_messages

    return result


# -------------------------------------------------
# FILE INPUT ENDPOINT (MULTIPART ONLY)
# -------------------------------------------------
@app.post("/process/file")
async def process_file(
    file: UploadFile = File(...),
    session_id: str = Form(...)
):
    temp_path = f"temp_{file.filename}"

    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    user_input = read_pdf(temp_path)
    os.remove(temp_path)

    agent_type = "Invoice Processing"

    # 🧠 Run agent brain WITH memory
    result = think_and_plan(
        user_input=user_input,
        agent_type=agent_type,
        session_id=session_id
    )

    # 💾 Save memory
    save_memory(session_id, agent_type, user_input)

    # 📥 Load memory to return
    memory_rows = load_memory(session_id)
    memory_messages = [msg for _, msg in memory_rows]

    result["memory"] = memory_messages

    return result
