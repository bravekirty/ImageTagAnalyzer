FROM python:3.13-slim

WORKDIR /app

RUN pip install poetry

COPY shared /shared
COPY analytics-service/pyproject.toml analytics-service/poetry.lock .

RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-root

COPY db-setup/db-setup.py .

CMD ["python", "db-setup.py"]
