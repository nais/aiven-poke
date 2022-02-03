ARG PY_VERSION=3.9
ARG KUBECTL_VERSION=v1.19.13
ARG EARTHLY_GIT_PROJECT_NAME
ARG BASEIMAGE=ghcr.io/$EARTHLY_GIT_PROJECT_NAME

FROM busybox

deps:
    FROM python:${PY_VERSION}-slim

    WORKDIR /app

    RUN pip install poetry
    ENV POETRY_VIRTUALENVS_IN_PROJECT=true

    COPY pyproject.toml poetry.lock .
    RUN poetry install --no-dev --no-root --no-interaction

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

tests:
    LOCALLY
    RUN poetry install --no-interaction && \
        poetry run prospector && \
        poetry run pytest

docker:
    FROM navikt/python:${PY_VERSION}
    ARG EARTHLY_GIT_SHORT_HASH
    ARG IMAGE_TAG=$EARTHLY_GIT_SHORT_HASH

    WORKDIR /app

    COPY --dir +deps/.venv .
    COPY --dir +build/aiven_poke .

    ENV PATH="/bin:/usr/bin:/usr/local/bin:/app/.venv/bin"

    CMD ["/app/.venv/bin/python", "-m", "aiven_poke"]

    SAVE IMAGE --push ${BASEIMAGE}:${IMAGE_TAG}
    SAVE IMAGE --push ${BASEIMAGE}:latest
