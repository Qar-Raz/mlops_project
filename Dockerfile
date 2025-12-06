# 1. Base Image
FROM python:3.11-slim as builder

# Install basic tools
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    && rm -rf /var/lib/apt/lists/*

# Increase timeout
ENV PIP_DEFAULT_TIMEOUT=1000

# 2. Install Python Build Tools
RUN pip install pip-tools wheel

# 3. Setup Work Directory
WORKDIR /app

# 4. Install Dependencies
COPY backend/requirements.txt ./

# Install requirements (using the heavy list) with pre-built wheels to be fast
RUN pip install --no-cache-dir -r requirements.txt \
    --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu

# 5. Runtime Stage
FROM python:3.11-slim

RUN useradd --create-home appuser
USER appuser
WORKDIR /home/appuser/app

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY ./backend ./backend
COPY ./class_names.txt .

EXPOSE 8000

# Healthcheck disabled - not needed for metrics monitoring
# HEALTHCHECK CMD curl --fail http://localhost:8000/health || exit 1

# Point to the real app
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]