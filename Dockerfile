FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app

CMD ["sh", "-c", "gunicorn --chdir app --bind 0.0.0.0:${PORT:-8080} main:app"]
