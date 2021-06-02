FROM python:3.9.5-alpine3.13

MAINTAINER Jonas Gröger <jonas@huntun.de>

ENV PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PYTHONDONTWRITEBYTECODE=1 \
    \
    PIP_NO_CACHE_DIR=yes \
    PIP_DISABLE_PIP_VERSION_CHECK=yes \
    PIP_DEFAULT_TIMEOUT=100 \
    \
    POETRY_NO_INTERACTION=yes \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_VERSION=1.1.6 \
    POETRY_HOME="/opt/poetry"

ENV PATH="$POETRY_HOME/bin:$PATH"

RUN apk --update-cache add \
    build-base \
    python3-dev \
    jpeg-dev \
    zlib-dev \
    curl \
    git

# Install Poetry version $POETRY_VERSION to $POETRY_HOME
RUN curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python

WORKDIR /app
COPY poetry.lock pyproject.toml ./
RUN poetry install --no-dev

COPY src/ docker-entrypoint /app/
EXPOSE 10000

ENTRYPOINT ["/app/docker-entrypoint"]
