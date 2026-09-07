# EduSimplify – Agentic AI Course Content Simplification Agent

> An IBM Granite-powered web application that simplifies complex academic content
> using a multi-agent AI pipeline, tailored to the student's proficiency level.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Architecture & Agent Workflow](#2-architecture--agent-workflow)
3. [Technologies Used](#3-technologies-used)
4. [Project Structure](#4-project-structure)
5. [Setup & Installation](#5-setup--installation)
6. [Configuration (IBM Credentials)](#6-configuration-ibm-credentials)
7. [Running the Application](#7-running-the-application)
8. [How to Use](#8-how-to-use)
9. [API Endpoints](#9-api-endpoints)
10. [Viva / Demo Guide](#10-viva--demo-guide)

---

## 1. Project Overview

**EduSimplify** is a student-friendly web application that takes complex academic text
(textbook chapters, lecture notes, research summaries) and transforms it into
easy-to-understand material at the student's chosen proficiency level
(**Beginner**, **Intermediate**, or **Advanced**).

It generates:
- ✅ Simple plain-language **explanation**
- ✅ Extracted **key concepts** with definitions
- ✅ Bullet-point **important points**
- ✅ Relatable real-world **examples**
- ✅ Concise **short summary**
- ✅ **Exam-focused questions** (MCQ + short-answer + application)
- ✅ Automated **quality review** with scores

The application is powered by **IBM Granite** language models accessed via
**IBM watsonx.ai**, and uses an **Agentic AI** design pattern where five
specialised agents each handle one phase of the pipeline.

---

## 2. Architecture & Agent Workflow

```
User Input (content + proficiency level)
          │
          ▼
┌─────────────────────────┐
│  Agent 1                │
│  Content Analyzer Agent │  → Identifies domain, main topics, complexity
└──────────┬──────────────┘
           │  (domain, topics)
           ▼
┌─────────────────────────┐
│  Agent 2                │
│  Simplification Agent   │  → Generates explanation, key concepts,
│                         │    important points, short summary
└──────────┬──────────────┘
           │  (key concepts list)
           ▼
┌─────────────────────────┐
│  Agent 3                │
│  Example Generator      │  → Creates 3 tailored real-world examples
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│  Agent 4                │
│  Exam Question Agent    │  → Produces MCQs, short-answer questions,
│                         │    and one application question
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│  Agent 5                │
│  Review Agent           │  → Quality-checks all outputs, assigns scores
│                         │    (Clarity, Completeness, Level Match, Usefulness)
└──────────┬──────────────┘
           │
           ▼
   JSON Response → Flask → Browser UI
```

Each agent:
- Has a **single responsibility** (SRP).
- Communicates via **structured prompts** sent to IBM Granite.
- Parses the model's response into a structured Python dict.
- Passes its output to the next agent in the chain via the **Orchestrator**.

---

## 3. Technologies Used

| Layer | Technology |
|---|---|
| AI Model | IBM Granite (`ibm/granite-13b-instruct-v2`) |
| AI Platform | IBM watsonx.ai (`/ml/v1/text/generation`) |
| Backend | Python 3.10+ · Flask 3.x |
| Frontend | HTML5 · CSS3 · Vanilla JavaScript (no frameworks) |
| HTTP Client | `requests` library |
| Configuration | `python-dotenv` + `config.py` |
| Templating | Jinja2 (via Flask) |

**No paid external services** are used beyond IBM watsonx (which has a free tier
for academic use). No database, no third-party JS frameworks.

---

## 4. Project Structure

```
EduSimplify/
├── app.py                      # Flask entry point, routes
├── orchestrator.py             # Coordinates all five agents
├── config.py                   # All configuration & credentials
├── llm_client.py               # IBM Granite API client (IAM token + generation)
│
├── agents/
│   ├── __init__.py
│   ├── content_analyzer.py     # Agent 1 – domain & topic analysis
│   ├── simplification_agent.py # Agent 2 – explanation, concepts, summary
│   ├── example_generator.py    # Agent 3 – real-world examples
│   ├── exam_question_agent.py  # Agent 4 – MCQ, short-answer, application
│   └── review_agent.py         # Agent 5 – quality scoring & review
│
├── templates/
│   └── index.html              # Main UI page (Jinja2)
│
├── static/
│   ├── css/style.css           # Responsive stylesheet
│   └── js/app.js               # Client-side JavaScript
│
├── requirements.txt            # Python dependencies
├── .env.example                # Template for environment variables
└── README.md                   # This file
```

---

## 5. Setup & Installation

### Prerequisites

- Python **3.10** or higher
- `pip` package manager
- An IBM Cloud account with access to **IBM watsonx.ai**

### Steps

```bash
# 1. Open a terminal in the EduSimplify folder
cd path/to/EduSimplify

# 2. Create a virtual environment (recommended)
python -m venv venv

# Windows:
venv\Scripts\activate

# macOS / Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

---

## 6. Configuration (IBM Credentials)

You need two values from IBM Cloud:

| Value | Where to find it |
|---|---|
| `IBM_API_KEY` | IBM Cloud → Manage → Access (IAM) → API keys → Create |
| `IBM_PROJECT_ID` | Your watsonx.ai project → Manage tab → Project ID |

### Option A – Edit `config.py` directly (simplest)

Open `config.py` and replace:
```python
IBM_API_KEY    = "YOUR_IBM_API_KEY_HERE"     # ← paste your key
IBM_PROJECT_ID = "YOUR_IBM_PROJECT_ID_HERE"  # ← paste your project ID
```

### Option B – Use a `.env` file

```bash
cp .env.example .env
# Then edit .env and fill in the values
```

Then add this line at the **top** of `config.py`:
```python
from dotenv import load_dotenv
load_dotenv()
```

> ⚠️ **Never commit your real API key** to version control.
> The `.env.example` file contains only placeholder values and is safe to commit.

---

## 7. Running the Application

```bash
# Make sure your virtual environment is active
python app.py
```

Open your browser and go to: **http://localhost:5000**

The status badge in the top-right corner will show:
- 🟢 **IBM Granite: Connected** — credentials are correct, ready to use.
- 🔴 **Credentials Not Set** — open `config.py` and add your credentials.

---

## 8. How to Use

1. **Paste** any academic text into the text area (or use a sample button).
2. **Select** your proficiency level: Beginner / Intermediate / Advanced.
3. Click **⚡ Simplify Content**.
4. Wait ~20–60 seconds while five agents process the content.
5. Browse the results using the five tabs:
   - **📖 Explanation** — plain-language explanation + key points + summary
   - **🔑 Key Concepts** — concept cards with definitions + topic tags
   - **💡 Examples** — 3 real-world examples
   - **📝 Exam Questions** — MCQs + short-answer + application question
   - **⭐ Review** — quality scores + pipeline execution log

---

## 9. API Endpoints

| Method | URL | Description |
|---|---|---|
| `GET` | `/` | Main UI |
| `GET` | `/health` | Server health + credential status |
| `GET` | `/api/status` | Returns whether credentials are configured |
| `POST` | `/api/simplify` | Runs the full agent pipeline |

### POST `/api/simplify` – Request Body
```json
{
  "content": "Your academic text here…",
  "level": "Beginner"
}
```
`level` must be one of: `"Beginner"`, `"Intermediate"`, `"Advanced"`.

### POST `/api/simplify` – Response
```json
{
  "error": false,
  "level": "Beginner",
  "domain": "Physics",
  "main_topics": ["Newton's Laws", "Force", "Mass"],
  "simple_explanation": "...",
  "key_concepts": ["Force: a push or pull on an object", "..."],
  "important_points": ["...", "..."],
  "short_summary": "...",
  "examples": [{"title": "...", "body": "..."}],
  "exam_mcq": [{"question": "...", "options": ["A) ...", ...], "answer": "A"}],
  "exam_short_answer": [{"question": "...", "hint": "..."}],
  "exam_application": "...",
  "review": {"clarity": 8, "completeness": 9, "level_match": 8, "usefulness": 9, "overall": 9, ...},
  "pipeline_log": ["Agent 1 (Content Analyzer): Done — domain=Physics", "..."]
}
```

---

## 10. Viva / Demo Guide

### Key Talking Points

**Q: What is Agentic AI?**
> Each agent is an autonomous unit with a single responsibility. Agents observe their
> inputs, reason using a language model, and act by producing structured outputs.
> Together they form a pipeline that solves a problem no single prompt could handle
> reliably alone.

**Q: Why five agents instead of one big prompt?**
> Decomposition improves output quality. Each agent can have a focused prompt,
> and failures are isolated. The Review Agent catches issues before the UI sees them.
> This mirrors real-world software engineering (microservices) applied to AI.

**Q: How does the IBM Granite integration work?**
> `llm_client.py` first fetches an IAM bearer token from `iam.cloud.ibm.com`,
> then calls the watsonx.ai `/ml/v1/text/generation` REST endpoint with the model ID,
> prompt, and generation parameters. Token caching avoids repeated IAM calls.

**Q: How does the application handle missing credentials?**
> `config.py` exports a `credentials_configured()` function that checks for
> placeholder strings. The Orchestrator calls it first; if false, it returns
> a descriptive error that the UI displays. No fake output is ever shown.

**Q: What makes this student-friendly?**
> Three proficiency levels, built-in sample texts, tabbed results, colour-coded
> MCQ answers, quality scores from the Review Agent, and a responsive design
> that works on mobile devices.
