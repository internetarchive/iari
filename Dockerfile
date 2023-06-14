FROM python:3.10-slim

LABEL maintainer="Dennis Priskorn <priskorn@riseup.net>"

ENV DOCKER=true

WORKDIR /app

COPY pyproject.toml .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir poetry && \
    poetry install && \
    mkdir /tmp/wikicitations-api/

CMD ["poetry run gunicorn -w 30 --bind unix:/tmp/wikicitations-api/ipc.sock wsgi:app --timeout 1000"]