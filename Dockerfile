FROM python:3.12-alpine

LABEL maintainer="Jonas Gröger <jonas@huntun.de>"

# Python: disable bytecode (.pyc) files
# https://docs.python.org/3.11/using/cmdline.html
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1

ENV PIP_NO_CACHE_DIR=yes \
    PIP_DISABLE_PIP_VERSION_CHECK=yes

ENV POETRY_HOME="/opt/poetry" \
    POETRY_VERSION=2.1.3 \
    POETRY_VIRTUALENVS_CREATE=false

# Poetry gets installed here
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
RUN curl -sSL "https://install.python-poetry.org" | python3 -

WORKDIR /app
COPY poetry.lock pyproject.toml ./
RUN poetry install

COPY src/ docker-entrypoint /app/
EXPOSE 10000

ENTRYPOINT ["/app/docker-entrypoint"]
