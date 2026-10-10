"""
Runs student-submitted code through a Judge0 API instead of local Docker
containers, for hosts that don't provide a Docker daemon (Render, Railway,
...). Selected with CODE_RUNNER_BACKEND=judge0; returns the same
ExecutionResult as the Docker runner so callers don't care which ran.

Judge0 does its own sandboxing (isolate: no network, CPU/memory limits).
Java submissions must declare `public class Main`, same as the Docker runner.
"""

import base64

import httpx

from app.config import settings
from app.services.code_runner import ExecutionResult

# https://ce.judge0.com/#statuses-and-languages-status-get
_STATUS_ACCEPTED = 3
_STATUS_TIME_LIMIT_EXCEEDED = 5
_STATUS_COMPILATION_ERROR = 6
_STATUS_INTERNAL_ERROR = 13


def _language_id(language: str) -> int | None:
    return {
        "python": settings.judge0_language_python,
        "java": settings.judge0_language_java,
        "ruby": settings.judge0_language_ruby,
    }.get(language)


def _headers() -> dict:
    headers = {"Content-Type": "application/json"}
    if not settings.judge0_api_key:
        return headers
    host = httpx.URL(settings.judge0_url).host
    if host.endswith("rapidapi.com"):
        headers["X-RapidAPI-Key"] = settings.judge0_api_key
        headers["X-RapidAPI-Host"] = host
    else:
        headers["X-Auth-Token"] = settings.judge0_api_key
    return headers


def _b64encode(text: str) -> str:
    return base64.b64encode(text.encode("utf-8")).decode("ascii")


def _b64decode(text: str | None) -> str:
    if not text:
        return ""
    return base64.b64decode(text).decode("utf-8", errors="replace")


async def run_judge0(code: str, language: str) -> ExecutionResult:
    language_id = _language_id(language)
    if language_id is None:
        return ExecutionResult(stdout="", stderr=f"Unsupported language: {language}", exit_code=1)

    payload = {
        "source_code": _b64encode(code),
        "language_id": language_id,
        "cpu_time_limit": settings.code_runner_timeout_seconds,
    }
    try:
        # wait=true blocks until the run finishes, so one request is enough.
        # base64 keeps non-UTF-8 output from breaking the JSON response.
        async with httpx.AsyncClient(timeout=settings.code_runner_timeout_seconds + 30) as client:
            resp = await client.post(
                f"{settings.judge0_url.rstrip('/')}/submissions",
                params={"base64_encoded": "true", "wait": "true"},
                headers=_headers(),
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()
    except httpx.HTTPStatusError as exc:
        status = exc.response.status_code
        detail = "daily quota reached — try again later" if status == 429 else exc.response.text[:200]
        return ExecutionResult(stdout="", stderr=f"Sandbox error: Judge0 returned {status}: {detail}", exit_code=1)
    except httpx.HTTPError as exc:
        return ExecutionResult(stdout="", stderr=f"Sandbox error: {exc!r}", exit_code=1)

    status_id = (data.get("status") or {}).get("id")
    stdout = _b64decode(data.get("stdout"))
    stderr = "".join(
        part
        for part in (
            _b64decode(data.get("compile_output")),
            _b64decode(data.get("stderr")),
        )
        if part
    )
    timed_out = status_id == _STATUS_TIME_LIMIT_EXCEEDED
    if timed_out:
        stderr += "\n[execution timed out]"
    elif status_id == _STATUS_INTERNAL_ERROR:
        stderr += f"\nSandbox error: {_b64decode(data.get('message'))}"

    exit_code = data.get("exit_code")
    if exit_code is None:
        # Compile errors / internal errors / timeouts carry no exit code.
        exit_code = 124 if timed_out else (0 if status_id == _STATUS_ACCEPTED else 1)
    if status_id == _STATUS_COMPILATION_ERROR:
        exit_code = exit_code or 1

    return ExecutionResult(stdout=stdout, stderr=stderr, exit_code=exit_code, timed_out=timed_out)
