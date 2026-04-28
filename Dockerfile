FROM python:3.13
#FROM python:3.13-slim

LABEL maintainer="Chris Lombardi <mojomonger@archive.org>"

WORKDIR /app

ENV PIP_DEFAULT_TIMEOUT=100
ENV POETRY_VIRTUALENVS_CREATE=false

#RUN pip install --no-cache-dir poetry && poetry config virtualenvs.create false
RUN pip install --no-cache-dir poetry
# --no-cache-dir saves space in docker image

COPY pyproject.toml poetry.lock ./

# Disable parallel downloads (KEY FIX)
RUN poetry config installer.parallel false

RUN poetry install -v --no-interaction --no-ansi --no-root
# maybe add -v?

COPY . ./

# Setup all the needed directories
RUN mkdir -p /tmp/wikicitations-api \
    json/articles \
    json/cache \
    json/cache/signals \
    json/dois \
    json/pdfs \
    json/references \
    json/urls \
    json/urls/archives \
    json/xhtmls

#CMD ["./debug_app.py"]
CMD ["gunicorn","-w", "9", "--bind", ":5000", "--timeout", "1500", "wsgi:app"]
