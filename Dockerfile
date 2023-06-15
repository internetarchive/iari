FROM python:3.10-slim

LABEL maintainer="Dennis Priskorn <priskorn@riseup.net>"

# Setup all the needed directories
RUN mkdir -p /tmp/wikicitations-api json/{articles,references,dois,urls,xhtmls,pdfs}

WORKDIR /app

RUN pip install --no-cache-dir poetry && poetry config virtualenvs.create false

COPY pyproject.toml .

RUN poetry install --no-interaction --no-ansi

COPY . ./

CMD ["./debug_app.py"]

