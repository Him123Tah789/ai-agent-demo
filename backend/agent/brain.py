from agent.matcher import (
    find_best_answer,
    DOCUMENT_QA_STORE,
    DOCUMENT_UPLOAD_COUNT
)


def generate_general_response(user_input: str, agent_type: str) -> str:
    """
    Safe, non-hallucinating, general responses when no documents exist.
    """
    text = user_input.lower()

    if any(word in text for word in ["hi", "hello", "help"]):
        return (
            "Hi! 👋 Yes, I can help you.\n\n"
            "You can ask me questions or upload documents "
            "so I can answer specifically based on them."
        )

    if "service" in text:
        return (
            "I can help explain services, workflows, or ideas.\n\n"
            "If you upload documents, I’ll answer strictly based on them."
        )

    if "how" in text or "what" in text:
        return (
            "That’s a good question 👍\n\n"
            "I can give general guidance, or you can upload documents "
            "for document-based answers."
        )

    return (
        "I’m here to help 🙂\n\n"
        "You can ask a question or upload documents "
        "to get precise answers."
    )


def think_and_plan(user_input: str, agent_type: str, session_id: str):

    user_input = user_input.strip()

    # -------------------------------------
    # CASE 1: NO DOCUMENTS UPLOADED (REAL CHECK)
    # -------------------------------------
    if DOCUMENT_UPLOAD_COUNT.get(session_id, 0) == 0:
        return {
            "thinking_steps": [
                "Read user question",
                "No documents uploaded in this session",
                "Generated general helpful response"
            ],
            "action": "Answered without documents",
            "confidence": 0.60,
            "human_needed": False,
            "explanation": generate_general_response(
                user_input, agent_type
            )
        }

    # -------------------------------------
    # CASE 2: DOCUMENTS EXIST → MATCHER
    # -------------------------------------
    match, score = find_best_answer(session_id, user_input)

    if match:
        return {
            "thinking_steps": [
                "Read user question",
                "Searched uploaded documents",
                "Compared question with document questions and answers",
                "Selected best matching answer"
            ],
            "action": "Answered using uploaded documents",
            "confidence": score,
            "human_needed": False,
            "explanation": match["answer"]
        }

    # -------------------------------------
    # CASE 3: DOCUMENTS EXIST BUT NO MATCH
    # -------------------------------------
    return {
        "thinking_steps": [
            "Read user question",
            "Searched uploaded documents",
            "No strong match found"
        ],
        "action": "Escalated to human agent",
        "confidence": 0.0,
        "human_needed": True,
        "explanation": (
            "I couldn’t find a relevant answer in the uploaded documents.\n\n"
            "Please rephrase your question or upload more documents."
        )
    }
