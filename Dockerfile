FROM python:3.12.2-alpine3.19

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
    POETRY_VERSION=1.7.1 \
    POETRY_HOME="/opt/poetry"

ENV PATH="$POETRY_HOME/bin:$PATH"

RUN apk add --no-cache -U \
    build-base \
    python3-dev \
    jpeg-dev \
    zlib-dev \
    freetype-dev \
    curl \
    git

# Install Poetry version $POETRY_VERSION to $POETRY_HOME
RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR /app
COPY poetry.lock pyproject.toml ./
RUN poetry install --no-root

COPY src/ docker-entrypoint /app/
EXPOSE 10000

ENTRYPOINT ["/app/docker-entrypoint"]
