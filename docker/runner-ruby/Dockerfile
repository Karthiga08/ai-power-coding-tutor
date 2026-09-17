# Sandbox image used to execute student-submitted Ruby code.
# Same isolation model as runner-python: no network, resource limits, and a
# non-root user, applied by backend/app/services/code_runner.py at run time.
FROM ruby:3.3-slim

RUN useradd --no-create-home --uid 10001 sandbox \
    && mkdir -p /sandbox && chown sandbox:sandbox /sandbox
USER sandbox

WORKDIR /sandbox
