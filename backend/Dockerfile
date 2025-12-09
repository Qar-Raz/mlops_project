# syntax=docker/dockerfile:1
FROM python:3.11-slim

WORKDIR /backend

# 1. System Dependencies (Minimal)
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 2. Python Setup
RUN pip install --upgrade pip

# 3. Install Torch CPU (Cached)
# We only need torch (for sentence-transformers), not vision/audio
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install torch --index-url https://download.pytorch.org/whl/cpu

# 4. Install Requirements
COPY requirements.txt .
# Filter out torch to prevent redownload, then install deps
RUN --mount=type=cache,target=/root/.cache/pip \
    grep -v "torch" requirements.txt > req_clean.txt && \
    pip install -r req_clean.txt

# 5. Copy Models
COPY models /backend/models

# 6. Env Vars
ENV MODEL_DIR=/backend/models

# 7. Copy App
COPY . .

EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
