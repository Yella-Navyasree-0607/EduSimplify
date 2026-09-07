"""
Agent 5 – Review Agent
========================
Responsibility:
  • Quality-check the outputs from all other agents.
  • Verify coherence, completeness, and level-appropriateness.
  • Produce a final confidence score and any improvement notes.
  • This agent is the last in the pipeline and acts as a gatekeeper.
"""

from llm_client import call_granite


REVIEW_PROMPT_TEMPLATE = """\
You are a quality-review agent for educational content.

STUDENT PROFICIENCY LEVEL: {level}
SUBJECT DOMAIN: {domain}

You have been given:
- Simple Explanation: {explanation}
- Key Concepts (count): {concept_count}
- Important Points (count): {point_count}
- Examples (count): {example_count}
- Exam Questions (MCQ count): {mcq_count}

Evaluate the overall output on these dimensions:
1. Clarity – Is the explanation clear for a {level} student?
2. Completeness – Are all sections adequately covered?
3. Level Appropriateness – Is the difficulty matched to {level}?
4. Usefulness – Will a student find this genuinely helpful?

Respond EXACTLY in this format:
CLARITY_SCORE: <1-10>
COMPLETENESS_SCORE: <1-10>
LEVEL_SCORE: <1-10>
USEFULNESS_SCORE: <1-10>
OVERALL_SCORE: <1-10>
REVIEW_NOTE: <1-2 sentences summarising the quality of the output>
IMPROVEMENT_TIP: <one actionable tip to improve the material further>
"""


def review_output(
    level: str,
    domain: str,
    explanation: str,
    concept_count: int,
    point_count: int,
    example_count: int,
    mcq_count: int,
) -> dict:
    """
    Review the combined output of all agents.

    Returns
    -------
    dict with keys: clarity, completeness, level_match, usefulness,
                    overall, review_note, improvement_tip, raw_review
    """
    short_explanation = (explanation[:200] + "…") if len(explanation) > 200 else explanation

    prompt = REVIEW_PROMPT_TEMPLATE.format(
        level=level,
        domain=domain,
        explanation=short_explanation,
        concept_count=concept_count,
        point_count=point_count,
        example_count=example_count,
        mcq_count=mcq_count,
    )
    raw = call_granite(prompt)

    result = {
        "clarity": 0,
        "completeness": 0,
        "level_match": 0,
        "usefulness": 0,
        "overall": 0,
        "review_note": "",
        "improvement_tip": "",
        "raw_review": raw,
    }

    for line in raw.splitlines():
        stripped = line.strip()
        if stripped.startswith("CLARITY_SCORE:"):
            result["clarity"] = _parse_score(stripped)
        elif stripped.startswith("COMPLETENESS_SCORE:"):
            result["completeness"] = _parse_score(stripped)
        elif stripped.startswith("LEVEL_SCORE:"):
            result["level_match"] = _parse_score(stripped)
        elif stripped.startswith("USEFULNESS_SCORE:"):
            result["usefulness"] = _parse_score(stripped)
        elif stripped.startswith("OVERALL_SCORE:"):
            result["overall"] = _parse_score(stripped)
        elif stripped.startswith("REVIEW_NOTE:"):
            result["review_note"] = stripped.replace("REVIEW_NOTE:", "").strip()
        elif stripped.startswith("IMPROVEMENT_TIP:"):
            result["improvement_tip"] = stripped.replace("IMPROVEMENT_TIP:", "").strip()

    return result


def _parse_score(line: str) -> int:
    """Extract numeric score from a line like 'CLARITY_SCORE: 8'."""
    try:
        return int(line.split(":", 1)[1].strip().split()[0])
    except (IndexError, ValueError):
        return 0
