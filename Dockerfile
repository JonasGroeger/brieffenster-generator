FROM alpine:3.13

MAINTAINER Jonas Gröger <jonas@huntun.de>

#ENV LIBRARY_PATH=/lib:/usr/lib
RUN apk --no-cache add python3 py3-pip && \
    #apk --no-cache add build-base python3-dev jpeg-dev zlib-dev && \
    pip install --upgrade pip pipenv

COPY /src /app/
COPY Pipfile* /app/
RUN ls -la app

WORKDIR /app

RUN pipenv install --system --deploy
