# Sandbox image used to execute student-submitted Python code (report 6.5).
# Runs with no network, a read-only root filesystem, a tmpfs /sandbox, and a
# non-root user — see backend/app/services/code_runner.py for how it's invoked.
FROM python:3.11-slim

RUN useradd --no-create-home --uid 10001 sandbox \
    && mkdir -p /sandbox && chown sandbox:sandbox /sandbox
USER sandbox

WORKDIR /sandbox
