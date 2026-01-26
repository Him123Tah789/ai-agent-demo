from openai import OpenAI
import json
from agent.db import load_memory

client = OpenAI()

def think_and_plan(user_input, agent_type, session_id):
    # -----------------------------
    # 1. Load per-user memory from DB
    # -----------------------------
    past_memory = load_memory(session_id)

    memory_block = ""
    if past_memory:
        memory_block = "Previous interactions I remember:\n"
        for i, (a_type, msg) in enumerate(past_memory, 1):
            memory_block += f"{i}. ({a_type}) {msg}\n"

    # -----------------------------
    # 2. Build prompt with memory
    # -----------------------------
    prompt = f"""
You are an AI {agent_type} agent.

{memory_block}

Current user message:
\"\"\"{user_input}\"\"\"

Your task:
- Understand the input
- Use previous interactions if relevant
- Explain your thinking in clear, human-friendly steps
- Decide an action
- Estimate confidence
- Decide if human help is needed

Return ONLY valid JSON in this exact format:

{{
  "issue_type": "string",
  "thinking_steps": ["step 1", "step 2", "step 3"],
  "action": "string",
  "confidence": 0.0,
  "human_needed": false,
  "explanation": "short explanation that mentions memory if relevant"
}}

IMPORTANT:
- No markdown
- No commentary
- JSON only
"""

    # -----------------------------
    # 3. Call OpenAI
    # -----------------------------
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You must return valid JSON only."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    raw_output = response.choices[0].message.content.strip()

    # 🔍 DEBUG LOG
    print("\n----- RAW LLM OUTPUT -----")
    print(raw_output)
    print("--------------------------\n")

    # -----------------------------
    # 4. Parse safely
    # -----------------------------
    try:
        result = json.loads(raw_output)
    except Exception:
        result = {
            "issue_type": "unknown",
            "thinking_steps": [
                "Received input",
                "Reviewed previous interactions",
                "Model returned invalid format"
            ],
            "action": "Escalated to human agent",
            "confidence": 0.0,
            "human_needed": True,
            "explanation": "The AI could not return a valid structured response."
        }

    return result
