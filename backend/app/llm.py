"""
llm.py — LLM Abstraction Layer

Switches between Ollama (local, unlimited) and Groq (production, fast).
Controlled by the LLM_PROVIDER env var.

Dev workflow:   LLM_PROVIDER=ollama  → hits localhost:11434 (free, unlimited)
Prod/interview: LLM_PROVIDER=groq   → hits Groq API (14K req/day free, 500 tok/s)

Why this abstraction?
  - Single function the entire agent calls: llm_generate(prompt) → str
  - Swap providers with one env var, zero code changes
  - Interview line: "Dual-stack LLM — Ollama for unlimited dev,
    Groq for production speed. Zero vendor lock-in."
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

# ── Config ────────────────────────────────────────────────────────

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")  # "ollama" or "groq"

# Ollama
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")

# Groq
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")


# ── Ollama ────────────────────────────────────────────────────────


def _ollama_generate(prompt: str) -> str:
    """Calls local Ollama server. No API key needed."""
    try:
        resp = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.1},
            },
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json()["response"].strip()
    except Exception as e:
        return f"[Ollama error: {e}]"


# ── Groq ──────────────────────────────────────────────────────────


def _groq_generate(prompt: str) -> str:
    """Calls Groq API. Needs GROQ_API_KEY env var."""
    try:
        from groq import Groq

        client = Groq(api_key=GROQ_API_KEY)
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=1024,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[Groq error: {e}]"


# ── Public API ────────────────────────────────────────────────────


def llm_generate(prompt: str) -> str:
    """
    Single entry point for the entire agent.
    Routes to Ollama or Groq based on LLM_PROVIDER env var.
    """
    if LLM_PROVIDER == "groq":
        return _groq_generate(prompt)
    else:
        return _ollama_generate(prompt)


# ── Test ──────────────────────────────────────────────────────────
# cd backend && uv run python -m app.llm

if __name__ == "__main__":
    print(f"Provider: {LLM_PROVIDER}")
    print(f"Model: {OLLAMA_MODEL if LLM_PROVIDER == 'ollama' else GROQ_MODEL}")
    print()
    answer = llm_generate("What is 2 + 2? Answer in one word.")
    print(f"Response: {answer}")
