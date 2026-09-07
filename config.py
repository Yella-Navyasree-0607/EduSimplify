"""
EduSimplify – Configuration
============================
All IBM watsonx / Granite credentials go here.
Set them in .env (copy from .env.example) or export them as environment variables.

DEMO_MODE
---------
When IBM credentials are absent (the default for development), the application
automatically runs in DEMO MODE.  All five agents return rich pre-written
responses so the complete workflow can be demonstrated without any API keys.

To force demo mode explicitly:   set DEMO_MODE=true   in .env or environment.
To force live mode (requires credentials): set DEMO_MODE=false.
"""

import os
try:
    from dotenv import load_dotenv
    # override=False so real env vars always win over .env
    load_dotenv(override=False)
except ImportError:
    pass  # python-dotenv is optional; env vars / config.py values take precedence

# ─────────────────────────────────────────────────────────────────────────────
#  IBM watsonx.ai credentials
#  Get these from: https://cloud.ibm.com/
#  1. Create a watsonx.ai project
#  2. Generate an API key under Manage → Access (IAM) → API keys
#  3. Copy your Project ID from your watsonx project settings
# ─────────────────────────────────────────────────────────────────────────────
IBM_API_KEY      = os.getenv("IBM_API_KEY",      "YOUR_IBM_API_KEY_HERE")
IBM_PROJECT_ID   = os.getenv("IBM_PROJECT_ID",   "YOUR_IBM_PROJECT_ID_HERE")
IBM_REGION       = os.getenv("IBM_REGION",       "us-south")   # e.g. us-south, eu-de

# Derived endpoint (do not change unless IBM changes their URL scheme)
IBM_IAM_URL      = "https://iam.cloud.ibm.com/identity/token"
IBM_WX_URL       = f"https://{IBM_REGION}.ml.cloud.ibm.com"

# ─────────────────────────────────────────────────────────────────────────────
#  Model selection
#  IBM Granite models available on watsonx.ai:
#    granite-13b-instruct-v2   – flagship instruction-tuned model
#    granite-3-8b-instruct     – lighter, faster
# ─────────────────────────────────────────────────────────────────────────────
GRANITE_MODEL_ID = os.getenv("GRANITE_MODEL_ID", "ibm/granite-13b-instruct-v2")

# ─────────────────────────────────────────────────────────────────────────────
#  Generation parameters (sensible defaults – adjust as needed)
# ─────────────────────────────────────────────────────────────────────────────
GENERATION_PARAMS = {
    "decoding_method": "greedy",
    "max_new_tokens":  1024,
    "min_new_tokens":  50,
    "stop_sequences":  [],
    "repetition_penalty": 1.1,
}

# ─────────────────────────────────────────────────────────────────────────────
#  Flask settings
# ─────────────────────────────────────────────────────────────────────────────
FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "edusimplify-dev-secret-2024")
FLASK_DEBUG      = os.getenv("FLASK_DEBUG", "false").lower() == "true"
FLASK_PORT       = int(os.getenv("FLASK_PORT", "5000"))

# ─────────────────────────────────────────────────────────────────────────────
#  Helper – detect whether real credentials have been supplied
# ─────────────────────────────────────────────────────────────────────────────
def credentials_configured() -> bool:
    """Return True only when real (non-placeholder) credentials are present.

    Reads directly from os.environ at call time so that values loaded by
    python-dotenv (or set after module import) are always reflected correctly.
    """
    key = os.getenv("IBM_API_KEY",    "").strip()
    pid = os.getenv("IBM_PROJECT_ID", "").strip()
    placeholder = {"", "YOUR_IBM_API_KEY_HERE", "YOUR_IBM_PROJECT_ID_HERE"}
    return key not in placeholder and pid not in placeholder


# ─────────────────────────────────────────────────────────────────────────────
#  Demo Mode
#  Automatically active when credentials are absent.
#  Set DEMO_MODE=true to force it on; DEMO_MODE=false to force it off.
# ─────────────────────────────────────────────────────────────────────────────
def demo_mode_active() -> bool:
    """Return True when the application should use demo responses.

    Priority:
      1. DEMO_MODE=true  → always demo
      2. DEMO_MODE=false → always live (credentials still required)
      3. No DEMO_MODE set → auto: demo when credentials are absent
    """
    explicit = os.getenv("DEMO_MODE", "").strip().lower()
    if explicit == "true":
        return True
    if explicit == "false":
        return False
    # Auto-detect: demo mode when no real credentials are configured
    return not credentials_configured()
