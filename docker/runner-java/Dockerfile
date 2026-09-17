# Sandbox image used to compile and execute student-submitted Java code.
# Same isolation model as runner-python: no network, resource limits, and a
# non-root user, applied by backend/app/services/code_runner.py at run time.
FROM eclipse-temurin:21-jdk-alpine

RUN adduser -D -u 10001 sandbox \
    && mkdir -p /sandbox && chown sandbox:sandbox /sandbox
USER sandbox

WORKDIR /sandbox
