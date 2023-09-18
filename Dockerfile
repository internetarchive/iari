FROM python:3.10-slim

LABEL maintainer="Dennis Priskorn <priskorn@riseup.net>"

WORKDIR /app

RUN pip install --no-cache-dir poetry && poetry config virtualenvs.create false
# --no-cache-dir saves space in docker image

COPY pyproject.toml .

RUN poetry install -v --no-interaction --no-ansi
# maybe add -v?

COPY . ./

# Setup all the needed directories
RUN mkdir -p /tmp/wikicitations-api json/articles json/references json/dois json/urls json/xhtmls json/pdfs

#CMD ["./debug_app.py"]
CMD ["gunicorn","-w", "4", "--bind", ":5000", "--timeout", "1500", "wsgi:app"]
