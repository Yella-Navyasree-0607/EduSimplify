"""
Agent 3 – Example Generator Agent
====================================
Responsibility:
  • Generate 2-3 concrete, relatable real-world examples for the content.
  • Tailor example difficulty and context to the student's level.
  • Examples should be self-contained mini-stories or analogies.
"""

from llm_client import call_granite


EXAMPLE_PROMPT_TEMPLATE = """\
You are a creative educational example generator.

STUDENT PROFICIENCY LEVEL: {level}
SUBJECT DOMAIN: {domain}
KEY CONCEPTS: {concepts}

Original content:
\"\"\"
{content}
\"\"\"

Generate exactly 3 easy-to-understand, relatable examples that illustrate the key ideas
from the content above. Tailor each example to a {level} level student.

Use EXACTLY this format for each example:

EXAMPLE 1:
Title: <catchy title>
<2-4 sentence example using everyday language, real-world scenarios, or simple analogies>

EXAMPLE 2:
Title: <catchy title>
<2-4 sentence example>

EXAMPLE 3:
Title: <catchy title>
<2-4 sentence example>
"""


def generate_examples(raw_content: str, level: str, domain: str, concepts: list) -> list:
    """
    Generate real-world examples for the content.

    Parameters
    ----------
    raw_content : str   – original academic text
    level       : str   – proficiency level
    domain      : str   – subject domain
    concepts    : list  – key concepts from SimplificationAgent

    Returns
    -------
    list of dicts, each with keys: title, body
    """
    concepts_str = ", ".join(concepts[:5]) if concepts else "core ideas in the content"

    prompt = EXAMPLE_PROMPT_TEMPLATE.format(
        content=raw_content.strip(),
        level=level,
        domain=domain,
        concepts=concepts_str,
    )
    raw = call_granite(prompt)

    examples = []
    current_title = ""
    current_body_lines: list[str] = []

    for line in raw.splitlines():
        stripped = line.strip()
        if stripped.startswith("EXAMPLE") and stripped.endswith(":"):
            # Save previous example
            if current_title:
                examples.append({
                    "title": current_title,
                    "body": " ".join(current_body_lines).strip(),
                })
            current_title = ""
            current_body_lines = []
        elif stripped.startswith("Title:"):
            current_title = stripped.replace("Title:", "").strip()
        elif stripped and current_title:
            current_body_lines.append(stripped)

    # Capture the last example
    if current_title:
        examples.append({
            "title": current_title,
            "body": " ".join(current_body_lines).strip(),
        })

    return examples
