FROM python:3.14-slim AS build

COPY --from=ghcr.io/astral-sh/uv:0.9.21 /uv /bin/

ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never \
    UV_PYTHON=python3.14 \
    UV_PROJECT_ENVIRONMENT=/app/venv

# Install dependencies before copying source for better layer caching
RUN --mount=type=cache,target=/root/.cache \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync \
        --locked \
        --no-dev \
        --no-install-project

COPY src/ /src/
COPY README.md LICENSE.md /

RUN --mount=type=cache,target=/root/.cache \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync \
        --locked \
        --no-dev \
        --no-editable


FROM python:3.14-slim AS runtime

LABEL maintainer="Jonas Gröger <jonas@huntun.de>"

RUN groupadd -r app && useradd -r -d /app -g app -N app

COPY --from=build /app/venv /app/venv
COPY docker-entrypoint.sh /

ENV VIRTUAL_ENV=/app/venv \
    PATH=/app/venv/bin:$PATH

WORKDIR /app

RUN /app/venv/bin/python -c 'import brieffenster_generator'

STOPSIGNAL SIGINT
EXPOSE 10000

USER app
ENTRYPOINT ["/docker-entrypoint.sh"]
