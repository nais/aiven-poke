VERSION 0.8

ARG --global PY_VERSION=3.12
ARG --global BASEIMAGE=europe-north1-docker.pkg.dev/nais-io/nais/images/aiven-poke

FROM busybox

deps:
    FROM python:${PY_VERSION}-slim

    WORKDIR /app

    RUN pip install poetry
    ENV POETRY_VIRTUALENVS_IN_PROJECT=true

    COPY pyproject.toml poetry.lock .
    RUN poetry install --only main --no-root --no-interaction

    SAVE ARTIFACT .venv
    SAVE IMAGE --cache-hint


build:
    FROM +deps

    RUN poetry install --no-root --no-interaction

    COPY --dir .prospector.yaml aiven_poke tests .
    RUN poetry install --no-interaction && \
        poetry run prospector && \
        poetry run pytest

    SAVE ARTIFACT aiven_poke
    SAVE IMAGE --cache-hint

test:
    LOCALLY
    RUN poetry install --no-interaction && \
        poetry run prospector && \
        poetry run pytest

docker:
    FROM python:${PY_VERSION}-slim

    WORKDIR /app

    COPY --dir +deps/.venv .
    COPY --dir +build/aiven_poke .

    ENV PATH="/bin:/usr/bin:/usr/local/bin:/app/.venv/bin"
    ENV PYTHONPATH=/app/.venv/lib/python${PY_VERSION}/site-packages

    ENTRYPOINT ["python", "-m", "aiven_poke"]

    ARG EARTHLY_GIT_SHORT_HASH
    ARG IMAGE_TAG=$EARTHLY_GIT_SHORT_HASH
    SAVE IMAGE --push ${BASEIMAGE}:${IMAGE_TAG} ${BASEIMAGE}:latest
