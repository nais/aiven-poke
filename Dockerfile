ARG PY_VERSION=3.12

FROM python:${PY_VERSION}-slim AS deps

WORKDIR /app

RUN pip install poetry
ENV POETRY_VIRTUALENVS_IN_PROJECT=true

COPY pyproject.toml poetry.lock ./
RUN poetry install --only main --no-root --no-interaction

FROM deps AS build

RUN poetry install --no-root --no-interaction

COPY .prospector.yaml ./
COPY tests ./tests/
COPY aiven_poke ./aiven_poke/
RUN poetry install --no-interaction && \
	poetry run prospector && \
	poetry run pytest

FROM python:${PY_VERSION}-slim AS docker

WORKDIR /app

COPY --from=deps /app/.venv ./.venv/
COPY --from=build /app/aiven_poke ./aiven_poke/

ENV PATH="/bin:/usr/bin:/usr/local/bin:/app/.venv/bin"

ARG PY_VERSION
ENV PYTHONPATH=/app/.venv/lib/python${PY_VERSION}/site-packages

RUN python3 -c "import aiven_poke" ## Minimal testing that imports actually work
ENTRYPOINT ["python", "-m", "aiven_poke"]
