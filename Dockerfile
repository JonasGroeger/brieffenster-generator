FROM python:3.12.0-alpine3.18

LABEL maintainer="Jonas Gröger <jonas@huntun.de>"

ENV PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PYTHONDONTWRITEBYTECODE=1 \
    \
    PIP_NO_CACHE_DIR=yes \
    PIP_DISABLE_PIP_VERSION_CHECK=yes \
    PIP_DEFAULT_TIMEOUT=100 \
    \
    POETRY_HOME="/opt/poetry" \
    POETRY_VERSION=1.7.1 \
    POETRY_VIRTUALENVS_CREATE=false

# Poetry gets installed here
ENV PATH="$POETRY_HOME/bin:$PATH"

RUN apk --update-cache add \
    build-base \
    python3-dev \
    jpeg-dev \
    zlib-dev \
    curl \
    git

RUN curl -sSL https://install.python-poetry.org | python -

WORKDIR /app
COPY poetry.lock pyproject.toml ./
RUN poetry install --only main --no-root

COPY src/ docker-entrypoint /app/
EXPOSE 10000

ENTRYPOINT ["/app/docker-entrypoint"]
