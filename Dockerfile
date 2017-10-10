FROM alpine:latest

MAINTAINER Jonas Gröger <brieffenster@jonas.huntun.de>

# Install some dependencies
RUN apk --no-cache add python3 && \
    pip3 install --upgrade pip

COPY /src /app/
COPY requirements.txt /app/
RUN ls /app
#RUN pip3 install --upgrade pip && pip3 install -r /app/requirements.txt
