FROM alpine:3.13

MAINTAINER Jonas Gröger <jonas@huntun.de>

ENV LIBRARY_PATH=/lib:/usr/lib
RUN apk --no-cache add python3 py3-pip &&  \
    apk --no-cache add build-base python3-dev jpeg-dev zlib-dev curl

COPY Pipfile* /app/

WORKDIR /app

RUN pip install pipenv
RUN pipenv install --system --deploy --ignore-pipfile

COPY /src /app/

CMD ["gunicorn", "wsgi:app", "--bind", "0.0.0.0:5000", "--workers", "4"]
