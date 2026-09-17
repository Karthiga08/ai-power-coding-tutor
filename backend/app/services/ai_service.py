"""
Context-aware AI tutor service (report section 6.4). Builds a single prompt
from the learner's question plus whatever course/problem/code context is
available, then calls whichever provider is configured (OpenAI or Gemini)
behind one common interface so the provider can be swapped via config alone.
"""

import httpx

from app.config import settings

SYSTEM_PROMPT = (
    "You are an AI programming tutor embedded in a coding education platform. "
    "Explain concepts clearly, point out bugs precisely, and suggest concrete "
    "improvements. Keep answers focused and avoid giving a full solution "
    "unless explicitly asked for one."
)


def build_prompt(
    message: str,
    context_type: str,
    lesson_content: str | None = None,
    problem_description: str | None = None,
    code: str | None = None,
) -> str:
    parts = [f"Student request ({context_type}): {message}"]
    if lesson_content:
        parts.append(f"\nRelevant lesson content:\n{lesson_content}")
    if problem_description:
        parts.append(f"\nProblem statement:\n{problem_description}")
    if code:
        parts.append(f"\nStudent's current code:\n```\n{code}\n```")
    return "\n".join(parts)


async def _call_openai(prompt: str) -> str:
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {settings.openai_api_key}"},
            json={
                "model": settings.openai_model,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.3,
            },
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]


async def _call_gemini(prompt: str) -> str:
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{settings.gemini_model}:generateContent?key={settings.gemini_api_key}",
            json={
                "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
                "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            },
        )
        resp.raise_for_status()
        data = resp.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]


async def ask_ai_tutor(prompt: str) -> str:
    if settings.ai_provider == "gemini":
        return await _call_gemini(prompt)
    return await _call_openai(prompt)
