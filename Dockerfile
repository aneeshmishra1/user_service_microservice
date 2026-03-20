
FROM python:3.12-slim

# Prevent Python from writing pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# Ensure logs go straight to Cloud Run logs.checking.####
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# ---------- System Dependencies ----------
# Install minimal OS dependencies required for pg8000 and security
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ---------- Copy Application ----------
COPY . .


# Cloud Run provides PORT env variable (default 8080)
ENV PORT=8081

# ---------- Run Application ----------
# Use gunicorn with uvicorn workers (recommended for Cloud Run)
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8081", "--workers", "2", "--threads", "4", "--timeout", "0", "app.main:app"]