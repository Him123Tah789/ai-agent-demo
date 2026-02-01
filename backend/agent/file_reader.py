from pypdf import PdfReader
import re


QUESTION_PATTERNS = (
    "what", "how", "why", "when", "where",
    "who", "which", "does", "do", "is", "are", "can"
)


def clean_line(line: str) -> str:
    line = re.sub(r"\s+", " ", line)
    return line.strip()


def is_question(line: str) -> bool:
    line_lower = line.lower()
    return (
        line_lower.endswith("?")
        or any(line_lower.startswith(w + " ") for w in QUESTION_PATTERNS)
    )


def read_pdf_to_qa(file_path: str):
    reader = PdfReader(file_path)
    raw_text = ""

    for page in reader.pages:
        text = page.extract_text()
        if text:
            raw_text += text + "\n"

    lines = [clean_line(l) for l in raw_text.split("\n") if clean_line(l)]

    qa_pairs = []
    current_question = None
    current_answer = []

    for line in lines:
        if is_question(line):
            # Save previous Q&A
            if current_question and len(current_answer) > 5:
                qa_pairs.append({
                    "question": current_question,
                    "answer": " ".join(current_answer)
                })

            current_question = line
            current_answer = []

        else:
            # Attach answer lines
            if current_question:
                current_answer.append(line)

    # Save last Q&A
    if current_question and len(current_answer) > 5:
        qa_pairs.append({
            "question": current_question,
            "answer": " ".join(current_answer)
        })

    return qa_pairs
