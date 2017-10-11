FROM alpine:latest

MAINTAINER Jonas Gröger <brieffenster@jonas.huntun.de>

ENV LIBRARY_PATH=/lib:/usr/lib
RUN apk --no-cache add python3 && \
    apk --no-cache add build-base python3-dev jpeg-dev zlib-dev && \
    pip3 install --upgrade pip pipenv

COPY /src /app/
COPY Pipfile.lock /app/

WORKDIR /app

RUN pipenv install --ignore-pipfile --system && rm -f Pipfile
