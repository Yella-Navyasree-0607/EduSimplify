"""
EduSimplify – Agentic Orchestrator
=====================================
Coordinates the five agents in a structured pipeline:

  User Input
      │
      ▼
  [Agent 1] Content Analyzer Agent
      │  domain, topics, complexity
      ▼
  [Agent 2] Simplification Agent
      │  explanation, key concepts, important points, summary
      ▼
  [Agent 3] Example Generator Agent
      │  real-world examples
      ▼
  [Agent 4] Exam Question Agent
      │  MCQs, short-answer, application question
      ▼
  [Agent 5] Review Agent
      │  quality scores + improvement tip
      ▼
  Final JSON response → Flask → UI

DEMO MODE
---------
When IBM credentials are not configured (or DEMO_MODE=true is set), the
pipeline runs the content-aware demo engine (demo_engine.py), which reads
the user's actual text and produces meaningful, contextual output through
all five agents — entirely in pure Python, no API keys required.
"""

import traceback
from config import credentials_configured, demo_mode_active
from demo_engine import run_demo_pipeline
from agents.content_analyzer   import analyze_content
from agents.simplification_agent import simplify_content
from agents.example_generator  import generate_examples
from agents.exam_question_agent import generate_exam_questions
from agents.review_agent       import review_output


def run_pipeline(raw_content: str, level: str) -> dict:
    """
    Execute the full multi-agent pipeline.

    Parameters
    ----------
    raw_content : str  – academic text entered by the student
    level       : str  – 'Beginner' | 'Intermediate' | 'Advanced'

    Returns
    -------
    dict containing the complete structured output or an error payload.
    """
    # ── Validate inputs ────────────────────────────────────────────────────
    if not raw_content or not raw_content.strip():
        return {"error": True, "error_type": "input", "message": "No content provided."}

    valid_levels = {"Beginner", "Intermediate", "Advanced"}
    if level not in valid_levels:
        return {"error": True, "error_type": "input",
                "message": f"Invalid level '{level}'. Choose from {valid_levels}."}

    # ── Demo Mode: run content-aware pipeline (no IBM credentials needed) ──
    if demo_mode_active():
        return run_demo_pipeline(raw_content, level)

    # ── Live Mode: run the real IBM Granite pipeline ───────────────────────
    pipeline_log = []

    try:
        # ── Step 1: Content Analyzer Agent ────────────────────────────────
        pipeline_log.append("Agent 1 (Content Analyzer): Running…")
        analysis = analyze_content(raw_content)
        domain   = analysis.get("domain", "General")
        pipeline_log.append(f"Agent 1 (Content Analyzer): Done — domain={domain}")

        # ── Step 2: Simplification Agent ──────────────────────────────────
        pipeline_log.append("Agent 2 (Simplification): Running…")
        simplification = simplify_content(raw_content, level, domain)
        pipeline_log.append("Agent 2 (Simplification): Done")

        # ── Step 3: Example Generator Agent ───────────────────────────────
        pipeline_log.append("Agent 3 (Example Generator): Running…")
        examples = generate_examples(
            raw_content, level, domain, simplification.get("key_concepts", [])
        )
        pipeline_log.append(f"Agent 3 (Example Generator): Done — {len(examples)} examples")

        # ── Step 4: Exam Question Agent ────────────────────────────────────
        pipeline_log.append("Agent 4 (Exam Questions): Running…")
        exam = generate_exam_questions(
            raw_content, level, domain, simplification.get("key_concepts", [])
        )
        pipeline_log.append(
            f"Agent 4 (Exam Questions): Done — {len(exam['mcq'])} MCQs, "
            f"{len(exam['short_answer'])} SA"
        )

        # ── Step 5: Review Agent ───────────────────────────────────────────
        pipeline_log.append("Agent 5 (Review): Running…")
        review = review_output(
            level=level,
            domain=domain,
            explanation=simplification.get("simple_explanation", ""),
            concept_count=len(simplification.get("key_concepts", [])),
            point_count=len(simplification.get("important_points", [])),
            example_count=len(examples),
            mcq_count=len(exam.get("mcq", [])),
        )
        pipeline_log.append(
            f"Agent 5 (Review): Done — overall score={review.get('overall', 'N/A')}/10"
        )

        # ── Assemble final response ────────────────────────────────────────
        return {
            "error": False,
            "demo_mode": False,
            "level": level,
            "pipeline_log": pipeline_log,

            # Agent 1
            "domain": domain,
            "main_topics": analysis.get("main_topics", []),
            "detected_complexity": analysis.get("complexity", level),
            "content_description": analysis.get("description", ""),

            # Agent 2
            "simple_explanation": simplification.get("simple_explanation", ""),
            "key_concepts": simplification.get("key_concepts", []),
            "important_points": simplification.get("important_points", []),
            "short_summary": simplification.get("short_summary", ""),

            # Agent 3
            "examples": examples,

            # Agent 4
            "exam_mcq": exam.get("mcq", []),
            "exam_short_answer": exam.get("short_answer", []),
            "exam_application": exam.get("application", ""),

            # Agent 5
            "review": review,
        }

    except Exception as exc:
        tb = traceback.format_exc()
        return {
            "error": True,
            "error_type": "pipeline",
            "message": str(exc),
            "traceback": tb,
            "pipeline_log": pipeline_log,
        }
