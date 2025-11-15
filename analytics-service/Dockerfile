FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

RUN pip install poetry

COPY shared /shared

COPY analytics-service/pyproject.toml analytics-service/poetry.lock .

RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-root

COPY analytics-service/ .

CMD ["gunicorn", "app.main:app", "--bind", "0.0.0.0:8002", "--worker-class", "uvicorn.workers.UvicornWorker", "--workers", "2"]
