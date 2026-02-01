from difflib import SequenceMatcher
import re

# In-memory document store (per session)
DOCUMENT_QA_STORE = {}


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def save_document(session_id: str, qa_pairs: list):
    """
    qa_pairs = [{"question": "...", "answer": "..."}]
    """
    if session_id not in DOCUMENT_QA_STORE:
        DOCUMENT_QA_STORE[session_id] = []

    for qa in qa_pairs:
        DOCUMENT_QA_STORE[session_id].append({
            "question": clean_text(qa["question"]),
            "answer": clean_text(qa["answer"])
        })


def extract_relevant_answer(answer: str, user_question: str) -> str:
    """
    Return only the most relevant sentence/paragraph from the answer
    """
    parts = re.split(r"[.\n]", answer)
    best_part = answer
    best_score = 0.0

    for part in parts:
        part = part.strip()
        if len(part) < 20:
            continue
        score = similarity(user_question, part)
        if score > best_score:
            best_score = score
            best_part = part

    return best_part.strip()


def find_best_answer(session_id: str, user_question: str):
    if session_id not in DOCUMENT_QA_STORE:
        return None, 0.0

    best_match = None
    best_score = 0.0

    for qa in DOCUMENT_QA_STORE[session_id]:
        score = similarity(user_question, qa["question"])

        if score > best_score:
            best_score = score
            best_match = qa

    if best_match:
        best_match = {
            "question": best_match["question"],
            "answer": extract_relevant_answer(
                best_match["answer"],
                user_question
            )
        }

    return best_match, round(best_score, 2)
