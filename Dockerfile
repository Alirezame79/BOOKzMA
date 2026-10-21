FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY migrations ./migrations
COPY alembic.ini .

RUN useradd --create-home --uid 10001 bot
USER bot

CMD ["sh", "-c", "alembic upgrade head && python -m BOOKzMA"]
