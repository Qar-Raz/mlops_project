# Backend Setup & Developer Guide

This guide explains how to set up the backend environment from scratch. It is designed to be **portable**, meaning it works the same way on every developer's machine using Docker.

## Prerequisites

1.  **Docker Desktop**: [Download & Install](https://www.docker.com/products/docker-desktop/)
    *   *Ensure it is running before proceeding.*
2.  **Git**: To clone the repository.

---

## Step-by-Step Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd mlops_project
```

### 2. Configure Credentials
To download the models from our S3 bucket, you need AWS credentials.

1.  Create a file named `.env` in the **root** of the project (`mlops_project/.env`).
2.  Add your AWS keys to it:
    ```env
    AWS_ACCESS_KEY_ID=your_access_key_here
    AWS_SECRET_ACCESS_KEY=your_secret_key_here
    ```
    *   *Note: This file is ignored by Git for security.*

### 3. Download & Prepare Models
We use a "one-click" command to set up the heavy model files. This command spins up a temporary Docker container to handle the downloading and optimization for you.

Run this in your terminal:
```bash
docker-compose run --rm backend python download_models.py
```

**What this does:**
1.  **Downloads** the raw model package from S3.
2.  **Converts** the Computer Vision model to ONNX format (optimized for CPU).
3.  **Downloads** the LLM (GGUF format) from HuggingFace.
4.  **Saves** all these files into the `models/` folder on your local machine.

*   *Wait for this to finish before proceeding. It may take a few minutes.*

### 4. Start the Application
Now that the models are ready, start the actual backend server:

```bash
docker-compose up --build
```

*   You will see logs scrolling. Wait for: `Uvicorn running on http://0.0.0.0:8000`

---

## Verification

Open your browser to check if it's working:

*   **Health Check**: [http://localhost:8000/](http://localhost:8000/)
    *   *Should see:* `{"message": "Plant Doctor Backend is running"}`
*   **API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
    *   *You can test the `/predict` endpoint here.*

### 5. Testing with the CLI Script
We have a Python script (`test_backend.py`) that simulates the frontend.

**Option A: Run Locally (Recommended)**
If you have Python installed on your machine:

1.  Open a new terminal in `mlops_project/backend`.
2.  Run the script:
    ```bash
    python test_backend.py
    ```
3.  When prompted, paste the full path to any image on your computer (e.g., `C:\Users\You\Desktop\plant.jpg`).

**Option B: Run via Docker (No Python Installed)**
If you don't want to install Python locally:

1.  Place a test image (e.g., `plant.jpg`) inside your `models/` folder.
2.  Run:
    ```bash
    docker-compose run --rm -e BASE_URL=http://backend:8000 backend python test_backend.py
    ```
3.  When asked for the path, type: `/app/models/plant.jpg`

---

## Stopping & Restarting

### Stopping
*   **Docker Desktop**: You can simply click the **Stop** button (square icon) next to the `mlops_project` container group.
*   **Terminal**: Press `Ctrl+C` to stop.

### Restarting (Without Rebuilding)
If you stopped the containers (but didn't remove them), you can turn them back on quickly without rebuilding or reinstalling anything.

*   **Command**:
    ```bash
    docker-compose start
    ```
*   **Docker Desktop**: Click the **Start** button (play icon).

*Note: If you removed the containers (using `docker-compose down`), you must run `docker-compose up` to create them again.*

---

## Troubleshooting

*   **"Volume not found"**: Ensure the `models/` folder exists in your project root and contains files like `flora_cv_onnx/` and `tinyllama...gguf`.
*   **AWS Errors**: Check that your `.env` file is in the project root and has the correct keys.
*   **Slow Performance**: The LLM runs on CPU. Responses may take 5-10 seconds depending on your hardware.

*   **Health Check:** [http://localhost:8000/](http://localhost:8000/) (Should return `{"message": "Plant Doctor Backend is running"}`)
*   **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs) (Interactive API documentation)

## Troubleshooting

*   **"Volume not found" or Model errors**: Ensure your `models/` folder is in the project root and contains the correct filenames.
*   **Port 8000 already in use**: If you have another service running on port 8000, you may need to stop it or modify the `ports` mapping in `docker-compose.yml`.
*   **Slow Performance**: The LLM runs on CPU. Inference might take a few seconds depending on your hardware.
