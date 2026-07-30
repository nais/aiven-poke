FROM cgr.dev/chainguard/python:latest-dev AS deps

WORKDIR /app

USER root
RUN apk add --no-cache sudo curl git ca-certificates build-base

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
ENV MISE_DATA_DIR="/mise"
ENV MISE_CONFIG_DIR="/mise"
ENV MISE_CACHE_DIR="/mise/cache"
ENV MISE_INSTALL_PATH="/usr/local/bin/mise"
ENV PATH="/mise/shims:$PATH"

RUN curl https://mise.run | sh
COPY mise.toml ./mise.toml
RUN mise trust -a && mise install

ENV UV_PROJECT_ENVIRONMENT=/app/.venv
ENV UV_LINK_MODE=copy

COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev --no-install-project

FROM deps AS build

RUN uv sync --no-install-project

COPY tests ./tests/
COPY aiven_poke ./aiven_poke/
RUN mise run check
RUN python3 -c "import aiven_poke" ## Minimal testing that imports actually work

FROM cgr.dev/chainguard/python:latest AS docker

WORKDIR /app
USER nonroot

COPY --from=deps /app/.venv ./.venv/
COPY --from=build /app/aiven_poke ./aiven_poke/

ENV PATH="/bin:/usr/bin:/usr/local/bin:/app/.venv/bin"

ARG PY_VERSION
ENV PYTHONPATH=/app/.venv/lib/python${PY_VERSION}/site-packages

ENTRYPOINT ["python", "-m", "aiven_poke"]
