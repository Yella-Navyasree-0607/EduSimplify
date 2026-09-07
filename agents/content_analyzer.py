"""
Agent 1 – Content Analyzer Agent
===================================
Responsibility:
  • Parse the raw academic content submitted by the user.
  • Identify the subject domain, key topics, and approximate complexity.
  • Produce a structured "content profile" passed to downstream agents.
"""

from llm_client import call_granite


ANALYZE_PROMPT_TEMPLATE = """\
You are an expert academic content analyzer.

A student has submitted the following academic text:
\"\"\"
{content}
\"\"\"

Your task:
1. Identify the subject/domain (e.g., Physics, Computer Science, Mathematics).
2. List the main topics covered (up to 6 bullet points).
3. Estimate the inherent complexity: Beginner / Intermediate / Advanced.
4. Write 2-3 sentences describing what this content is about.

Respond in the following structured format (use these exact section headings):
DOMAIN: <subject domain>
MAIN TOPICS:
- <topic 1>
- <topic 2>
...
COMPLEXITY: <Beginner | Intermediate | Advanced>
DESCRIPTION: <2-3 sentence description>
"""


def analyze_content(raw_content: str) -> dict:
    """
    Analyze the provided academic content.

    Parameters
    ----------
    raw_content : str  – the text pasted by the student

    Returns
    -------
    dict with keys: domain, main_topics, complexity, description, raw_analysis
    """
    prompt = ANALYZE_PROMPT_TEMPLATE.format(content=raw_content.strip())
    raw_analysis = call_granite(prompt)

    # ── Parse the structured response ────────────────────────────────────────
    result = {
        "domain": "General",
        "main_topics": [],
        "complexity": "Intermediate",
        "description": "",
        "raw_analysis": raw_analysis,
    }

    current_section = None
    for line in raw_analysis.splitlines():
        line = line.strip()
        if line.startswith("DOMAIN:"):
            result["domain"] = line.replace("DOMAIN:", "").strip()
        elif line.startswith("MAIN TOPICS:"):
            current_section = "topics"
        elif line.startswith("COMPLEXITY:"):
            result["complexity"] = line.replace("COMPLEXITY:", "").strip()
            current_section = None
        elif line.startswith("DESCRIPTION:"):
            result["description"] = line.replace("DESCRIPTION:", "").strip()
            current_section = None
        elif current_section == "topics" and line.startswith("-"):
            result["main_topics"].append(line.lstrip("- ").strip())

    return result
