FROM python:3.13
#FROM python:3.13-slim

LABEL maintainer="Chris Lombardi <mojomonger@yahoo.com>"

WORKDIR /app

RUN pip install --no-cache-dir poetry && poetry config virtualenvs.create false
# --no-cache-dir saves space in docker image

COPY pyproject.toml poetry.lock ./

RUN poetry install -v --no-interaction --no-ansi --no-root
# maybe add -v?

COPY . ./

# Setup all the needed directories
RUN mkdir -p /tmp/wikicitations-api json/articles json/references json/dois json/urls json/urls/archives json/xhtmls json/pdfs

#CMD ["./debug_app.py"]
CMD ["gunicorn","-w", "9", "--bind", ":5000", "--timeout", "1500", "wsgi:app"]
