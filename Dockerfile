FROM ubuntu:xenial

MAINTAINER Jonas Gröger <brieffenster@jonas.huntun.de>

RUN apt-get update && apt-get install --yes \
    python3 \
    python3-pip
RUN ls /app
COPY /src /app/

RUN ls /app
RUN pip3 install --upgrade pip3
RUN pip3 install -r /app/requirements.txt
