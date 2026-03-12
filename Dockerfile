ARG PY_VERSION=3.12

FROM python:${PY_VERSION}-slim AS deps

WORKDIR /app

RUN apt-get update  \
    && apt-get -y --no-install-recommends install sudo curl git ca-certificates build-essential

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
ENV MISE_DATA_DIR="/mise"
ENV MISE_CONFIG_DIR="/mise"
ENV MISE_CACHE_DIR="/mise/cache"
ENV MISE_INSTALL_PATH="/usr/local/bin/mise"
ENV PATH="/mise/shims:$PATH"

RUN curl https://mise.run | sh
COPY mise.toml ./mise.toml
COPY mise ./mise
RUN mise trust -a && mise install

ENV POETRY_VIRTUALENVS_IN_PROJECT=true

COPY pyproject.toml poetry.lock ./
RUN poetry install --only main --no-root --no-interaction

FROM deps AS build

RUN poetry install --no-root --no-interaction

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
