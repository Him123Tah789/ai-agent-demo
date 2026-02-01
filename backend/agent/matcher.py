import re
from difflib import SequenceMatcher

DOCUMENT_QA_STORE = {}
DOCUMENT_UPLOAD_COUNT = {}


def normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9 ]", "", text.lower()).strip()

def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, normalize(a), normalize(b)).ratio()

def save_document_qa(session_id: str, qa_pairs: list):
    if session_id not in DOCUMENT_QA_STORE:
        DOCUMENT_QA_STORE[session_id] = []

    DOCUMENT_QA_STORE[session_id].extend(qa_pairs)

    DOCUMENT_UPLOAD_COUNT[session_id] = (
        DOCUMENT_UPLOAD_COUNT.get(session_id, 0) + len(qa_pairs)
    )



def find_best_answer(session_id: str, user_question: str):
    if session_id not in DOCUMENT_QA_STORE or not DOCUMENT_QA_STORE[session_id]:
        return None, 0.0

    best_match = None
    best_score = 0.0

    for qa in DOCUMENT_QA_STORE[session_id]:
        q_score = similarity(user_question, qa["question"])
        a_score = similarity(user_question, qa["answer"])
        score = max(q_score, a_score)

        if score > best_score:
            best_score = score
            best_match = qa

    if best_score < 0.35:
        return None, round(best_score, 2)

    return best_match, round(best_score, 2)
