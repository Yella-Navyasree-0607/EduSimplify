"""
Agent 2 – Simplification Agent
=================================
Responsibility:
  • Take the raw content + the learner's chosen difficulty level.
  • Produce: plain-language explanation, key concepts, and important points.
  • Adapt vocabulary and depth to the chosen level.
"""

from llm_client import call_granite


SIMPLIFY_PROMPT_TEMPLATE = """\
You are a highly skilled educational content simplifier.

STUDENT PROFICIENCY LEVEL: {level}
SUBJECT DOMAIN: {domain}

Original academic content:
\"\"\"
{content}
\"\"\"

Your task is to simplify this content for a {level} level student.

Provide your response using EXACTLY these section headings:

SIMPLE EXPLANATION:
<Write a clear, easy-to-understand explanation suitable for {level} level. Use plain language, short sentences, and relatable comparisons. 150-200 words.>

KEY CONCEPTS:
- <Concept 1>: <one-sentence definition>
- <Concept 2>: <one-sentence definition>
- <Concept 3>: <one-sentence definition>
(include 4-6 key concepts)

IMPORTANT POINTS:
- <important point 1>
- <important point 2>
- <important point 3>
(include 4-6 important points)

SHORT SUMMARY:
<A concise 3-4 sentence summary capturing the essential idea of the content.>
"""


def simplify_content(raw_content: str, level: str, domain: str) -> dict:
    """
    Simplify the content for the given proficiency level.

    Parameters
    ----------
    raw_content : str  – original academic text
    level       : str  – 'Beginner' | 'Intermediate' | 'Advanced'
    domain      : str  – subject domain from ContentAnalyzerAgent

    Returns
    -------
    dict with keys: simple_explanation, key_concepts, important_points,
                    short_summary, raw_simplification
    """
    prompt = SIMPLIFY_PROMPT_TEMPLATE.format(
        content=raw_content.strip(),
        level=level,
        domain=domain,
    )
    raw = call_granite(prompt)

    result = {
        "simple_explanation": "",
        "key_concepts": [],
        "important_points": [],
        "short_summary": "",
        "raw_simplification": raw,
    }

    current_section = None
    buffer: list[str] = []

    def flush(section_key):
        if buffer:
            result[section_key] = "\n".join(buffer).strip()
            buffer.clear()

    for line in raw.splitlines():
        stripped = line.strip()

        if stripped.startswith("SIMPLE EXPLANATION:"):
            flush("simple_explanation")  # flush any leftover from a previous section
            current_section = "simple_explanation"
            after = stripped.replace("SIMPLE EXPLANATION:", "").strip()
            if after:
                buffer.append(after)
        elif stripped.startswith("KEY CONCEPTS:"):
            flush("simple_explanation")
            current_section = "key_concepts"
        elif stripped.startswith("IMPORTANT POINTS:"):
            flush("simple_explanation")  # in case SHORT SUMMARY line was missed
            current_section = "important_points"
        elif stripped.startswith("SHORT SUMMARY:"):
            flush("simple_explanation")
            current_section = "short_summary"
            after = stripped.replace("SHORT SUMMARY:", "").strip()
            if after:
                buffer.append(after)
        else:
            if current_section in ("key_concepts", "important_points"):
                if stripped.startswith("-"):
                    result[current_section].append(stripped.lstrip("- ").strip())
            elif current_section in ("simple_explanation", "short_summary"):
                if stripped:
                    buffer.append(stripped)

    # Flush any remaining buffer
    if current_section == "short_summary" and buffer:
        result["short_summary"] = "\n".join(buffer).strip()
    elif current_section == "simple_explanation" and buffer:
        flush("simple_explanation")

    return result
