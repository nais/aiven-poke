ARG PY_VERSION=3.13

FROM python:${PY_VERSION}-slim AS deps

WORKDIR /app

RUN apt-get update \
    && apt-get -y --no-install-recommends install sudo curl git ca-certificates build-essential

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

FROM python:${PY_VERSION}-slim AS docker

WORKDIR /app

COPY --from=deps /app/.venv ./.venv/
COPY --from=build /app/aiven_poke ./aiven_poke/

ENV PATH="/bin:/usr/bin:/usr/local/bin:/app/.venv/bin"

ARG PY_VERSION
ENV PYTHONPATH=/app/.venv/lib/python${PY_VERSION}/site-packages

RUN python3 -c "import aiven_poke" ## Minimal testing that imports actually work
ENTRYPOINT ["python", "-m", "aiven_poke"]
