FROM python:3.11-slim-bookworm

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install minimal runtime deps for Pillow
RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg62-turbo libpng16-16 \
    libfreetype6 libfontconfig1 \
    fonts-dejavu fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml poetry.lock* /app/
RUN pip install --no-cache-dir poetry && poetry install --without dev --no-root

COPY src /app/src

EXPOSE 8000

CMD ["sh", "-c", "poetry run uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000}"]

