"""
Runs student-submitted code inside a short-lived, locked-down Docker
container: no network, capped CPU/memory, hard timeout, killed and removed
afterwards. This is the sandbox described in report section 6.5, generalized
across languages (Python, Java, Ruby) via LANGUAGES below.

The Docker SDK is synchronous, so calls are pushed to a thread via
asyncio.to_thread so they don't block the FastAPI event loop.
"""

import asyncio
import tarfile
import io
import uuid

import docker
from docker.errors import ContainerError, DockerException

from app.config import settings


def _languages() -> dict:
    # Built lazily (not at import time) so settings are read fresh — the
    # values only matter at call time and this keeps tests/reloads simple.
    return {
        "python": {
            "image": settings.code_runner_image,
            "filename": "submission.py",
            "command": ["python", "submission.py"],
            "mem_limit": settings.code_runner_memory_limit,
        },
        "java": {
            "image": settings.code_runner_image_java,
            # The public class must be named Main to match the filename.
            "filename": "Main.java",
            "command": ["sh", "-c", "javac Main.java && java Main"],
            "mem_limit": settings.code_runner_memory_limit_java,
        },
        "ruby": {
            "image": settings.code_runner_image_ruby,
            "filename": "submission.rb",
            "command": ["ruby", "submission.rb"],
            "mem_limit": settings.code_runner_memory_limit,
        },
    }


class ExecutionResult:
    def __init__(self, stdout: str, stderr: str, exit_code: int, timed_out: bool = False):
        self.stdout = stdout
        self.stderr = stderr
        self.exit_code = exit_code
        self.timed_out = timed_out

    @property
    def passed(self) -> bool:
        return self.exit_code == 0 and not self.timed_out


def _build_tar(filename: str, content: str) -> io.BytesIO:
    stream = io.BytesIO()
    with tarfile.open(fileobj=stream, mode="w") as tar:
        data = content.encode("utf-8")
        info = tarfile.TarInfo(name=filename)
        info.size = len(data)
        tar.addfile(info, io.BytesIO(data))
    stream.seek(0)
    return stream


def _run_sync(code: str, language: str) -> ExecutionResult:
    lang = _languages().get(language)
    if lang is None:
        return ExecutionResult(stdout="", stderr=f"Unsupported language: {language}", exit_code=1)

    client = docker.from_env()
    container_name = f"tutor-run-{uuid.uuid4().hex[:12]}"
    container = None
    try:
        # Not read_only: the /sandbox overlay needs to be writable at
        # `create` time so put_archive() can inject the file below before
        # the container is started. A tmpfs mount here would only be
        # attached at start, which is too late for put_archive to target
        # it reliably. Isolation instead comes from network_disabled,
        # resource limits, no-new-privileges, and the non-root sandbox
        # user baked into the runner image — then the container (and its
        # writable layer) is destroyed immediately after in `finally`.
        container = client.containers.create(
            image=lang["image"],
            name=container_name,
            command=lang["command"],
            network_disabled=True,
            mem_limit=lang["mem_limit"],
            memswap_limit=lang["mem_limit"],
            cpu_period=100000,
            cpu_quota=settings.code_runner_cpu_quota,
            pids_limit=64,
            security_opt=["no-new-privileges"],
            stdin_open=True,
            detach=True,
        )
        container.put_archive("/sandbox", _build_tar(lang["filename"], code))
        container.start()

        try:
            result = container.wait(timeout=settings.code_runner_timeout_seconds)
            exit_code = result.get("StatusCode", 1)
            timed_out = False
        except Exception:
            container.kill()
            exit_code = 124
            timed_out = True

        stdout = container.logs(stdout=True, stderr=False).decode("utf-8", errors="replace")
        stderr = container.logs(stdout=False, stderr=True).decode("utf-8", errors="replace")
        if timed_out:
            stderr += "\n[execution timed out]"

        return ExecutionResult(stdout=stdout, stderr=stderr, exit_code=exit_code, timed_out=timed_out)
    except (ContainerError, DockerException) as exc:
        return ExecutionResult(stdout="", stderr=f"Sandbox error: {exc}", exit_code=1)
    finally:
        if container is not None:
            try:
                container.remove(force=True)
            except DockerException:
                pass


async def run_submission(code: str, language: str = "python") -> ExecutionResult:
    return await asyncio.to_thread(_run_sync, code, language)
