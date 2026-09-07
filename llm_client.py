"""
EduSimplify – IBM Granite LLM Client
======================================
Single place that handles:
  • IAM token acquisition (with in-memory caching)
  • Calling the watsonx.ai /text/generation endpoint
  • Falling back gracefully when credentials are not configured
"""

import time
import requests
from config import (
    IBM_API_KEY, IBM_PROJECT_ID, IBM_IAM_URL,
    IBM_WX_URL, GRANITE_MODEL_ID, GENERATION_PARAMS,
    credentials_configured,
)

# ── IAM token cache ────────────────────────────────────────────────────────
_token_cache: dict = {"token": None, "expires_at": 0}


def _get_iam_token() -> str:
    """Fetch a fresh IAM bearer token (cached for its lifetime - 60 s buffer)."""
    now = time.time()
    if _token_cache["token"] and now < _token_cache["expires_at"]:
        return _token_cache["token"]

    resp = requests.post(
        IBM_IAM_URL,
        data={
            "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
            "apikey": IBM_API_KEY,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    _token_cache["token"] = data["access_token"]
    # IBM tokens are typically valid for 3600 s; keep 60 s safety margin
    _token_cache["expires_at"] = now + data.get("expires_in", 3600) - 60
    return _token_cache["token"]


def call_granite(prompt: str) -> str:
    """
    Send *prompt* to IBM Granite and return the generated text.

    Raises
    ------
    RuntimeError  – when credentials are missing / not configured.
    requests.HTTPError – on non-2xx responses from watsonx.
    """
    if not credentials_configured():
        raise RuntimeError(
            "IBM credentials are not configured. "
            "Please set IBM_API_KEY and IBM_PROJECT_ID in config.py or as environment variables."
        )

    token = _get_iam_token()

    url = f"{IBM_WX_URL}/ml/v1/text/generation?version=2023-05-29"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    payload = {
        "model_id": GRANITE_MODEL_ID,
        "input": prompt,
        "parameters": GENERATION_PARAMS,
        "project_id": IBM_PROJECT_ID,
    }

    resp = requests.post(url, json=payload, headers=headers, timeout=120)
    resp.raise_for_status()
    result = resp.json()
    return result["results"][0]["generated_text"].strip()
