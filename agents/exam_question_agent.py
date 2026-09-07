"""
Agent 4 – Exam Question Agent
================================
Responsibility:
  • Generate exam-focused questions from the content.
  • Vary question types: MCQ, short-answer, and one application question.
  • Calibrate difficulty to the student's chosen level.
"""

from llm_client import call_granite


EXAM_PROMPT_TEMPLATE = """\
You are an expert academic examiner creating exam questions.

STUDENT PROFICIENCY LEVEL: {level}
SUBJECT DOMAIN: {domain}
KEY CONCEPTS: {concepts}

Content to base questions on:
\"\"\"
{content}
\"\"\"

Generate exam questions at {level} difficulty level. Use EXACTLY this format:

MULTIPLE CHOICE QUESTIONS:
Q1. <question text>
   A) <option A>
   B) <option B>
   C) <option C>
   D) <option D>
   Answer: <correct letter>

Q2. <question text>
   A) <option A>
   B) <option B>
   C) <option C>
   D) <option D>
   Answer: <correct letter>

Q3. <question text>
   A) <option A>
   B) <option B>
   C) <option C>
   D) <option D>
   Answer: <correct letter>

SHORT ANSWER QUESTIONS:
Q4. <question text>
Hint: <one-line hint>

Q5. <question text>
Hint: <one-line hint>

APPLICATION QUESTION:
Q6. <A practical / scenario-based question that tests deeper understanding>
"""


def generate_exam_questions(
    raw_content: str, level: str, domain: str, concepts: list
) -> dict:
    """
    Generate exam questions for the given content and level.

    Returns
    -------
    dict with keys: mcq (list of dicts), short_answer (list of dicts),
                    application (str), raw_questions
    """
    concepts_str = ", ".join(concepts[:5]) if concepts else "core ideas"

    prompt = EXAM_PROMPT_TEMPLATE.format(
        content=raw_content.strip(),
        level=level,
        domain=domain,
        concepts=concepts_str,
    )
    raw = call_granite(prompt)

    result = {
        "mcq": [],
        "short_answer": [],
        "application": "",
        "raw_questions": raw,
    }

    current_section = None
    current_q: dict | None = None
    current_options: list[str] = []
    current_answer = ""
    current_hint = ""
    current_q_text = ""

    def save_mcq():
        if current_q_text:
            result["mcq"].append({
                "question": current_q_text,
                "options": list(current_options),
                "answer": current_answer,
            })

    def save_sa():
        if current_q_text:
            result["short_answer"].append({
                "question": current_q_text,
                "hint": current_hint,
            })

    for line in raw.splitlines():
        stripped = line.strip()

        if stripped.startswith("MULTIPLE CHOICE QUESTIONS:"):
            current_section = "mcq"
        elif stripped.startswith("SHORT ANSWER QUESTIONS:"):
            if current_section == "mcq":
                save_mcq()
                current_q_text = ""; current_options.clear(); current_answer = ""
            current_section = "sa"
        elif stripped.startswith("APPLICATION QUESTION:"):
            if current_section == "sa":
                save_sa()
                current_q_text = ""; current_hint = ""
            current_section = "app"
        elif current_section == "mcq":
            if stripped.startswith(("Q1.", "Q2.", "Q3.")):
                if current_q_text:
                    save_mcq()
                current_q_text = stripped.split(".", 1)[1].strip()
                current_options.clear(); current_answer = ""
            elif stripped.startswith(("A)", "B)", "C)", "D)")):
                current_options.append(stripped)
            elif stripped.startswith("Answer:"):
                current_answer = stripped.replace("Answer:", "").strip()
        elif current_section == "sa":
            if stripped.startswith(("Q4.", "Q5.")):
                if current_q_text:
                    save_sa()
                current_q_text = stripped.split(".", 1)[1].strip()
                current_hint = ""
            elif stripped.startswith("Hint:"):
                current_hint = stripped.replace("Hint:", "").strip()
        elif current_section == "app":
            if stripped.startswith("Q6."):
                result["application"] = stripped.split(".", 1)[1].strip()
            elif result["application"] and stripped:
                result["application"] += " " + stripped

    # Flush any remaining items
    if current_section == "mcq" and current_q_text:
        save_mcq()
    if current_section == "sa" and current_q_text:
        save_sa()

    return result
