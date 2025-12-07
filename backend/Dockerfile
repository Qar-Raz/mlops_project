FROM python:3.11-slim

WORKDIR /backend

# 1. System Dependencies (Minimal)
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    curl \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 2. Python Setup
RUN pip install --no-cache-dir --upgrade pip

# 3. Install Torch CPU (Cached)
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# 4. Install Requirements
COPY requirements.txt .
# Filter out torch to prevent redownload, then install deps
RUN grep -v "torch" requirements.txt > req_clean.txt && \
    pip install --no-cache-dir -r req_clean.txt && \
    rm -rf /root/.cache/pip

# 5. Copy Models
COPY models /backend/models

# 6. Env Vars
ENV MODEL_DIR=/backend/models

# 7. Copy App
COPY . .

EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]