# 🚀 FloraBot Deployment Guide

This guide outlines the steps for teammates to build the production Docker image, handle model downloads, and deploy the application to the cloud.

## 📋 Prerequisites

Before you begin, ensure you have:
1.  **Docker Desktop** installed and running.
2.  **AWS Credentials** (Access Key ID & Secret Access Key) for the S3 bucket `mlopsmodel`.
3.  **Python 3.11+** installed locally.

---

## 🛠️ Step 1: Prepare the Backend

The backend requires large AI models that are not stored in Git. You must download them first.

**Why not use the temporary container method?**
*   *Previous Method*: `docker-compose run --rm backend python download_models.py` used a volume mount to save models to your host machine.
*   *Deployment Method*: We need the models inside the `backend/` folder so we can `COPY` them into the Docker image. Running the script directly is simpler for this purpose.

1.  **Navigate to the backend directory:**
    ```bash
    cd backend
    ```

2.  **Download the Models:**
    Run the download script. This will create a `models/` folder inside `backend/` and populate it with the necessary files (ONNX models, ChromaDB, GGUF LLM).
    ```bash
    # Ensure you have the dependencies installed first if running locally
    pip install boto3 python-dotenv huggingface_hub

    # Run the script
    python download_models.py
    ```
    *Note: You may need to set your AWS credentials as environment variables or in a `.env` file if the script prompts for them.*

3.  **Verify the Structure:**
    Ensure your `backend` folder looks like this:
    ```text
    backend/
    ├── models/               <-- Created by the script
    │   ├── flora_cv_onnx/
    │   ├── flora_rag_db/
    │   └── tinyllama...gguf
    ├── app.py
    ├── Dockerfile
    ├── requirements.txt
    └── ...
    ```

---

## 🐳 Step 2: Build the Docker Image

We will "bake" the models into the Docker image so it is self-contained and ready for the cloud.

1.  **Build the Image:**
    Run this command from the `backend/` directory:
    ```bash
    # Replace 'your-registry-username' with your Docker Hub or Cloud Registry username
    docker build -t your-registry-username/flora-backend:latest .
    ```

2.  **Test Locally (Optional but Recommended):**
    ```bash
    docker run -p 8000:8000 your-registry-username/flora-backend:latest
    ```
    *   Visit `http://localhost:8000/docs` to verify the API is running.
    *   Check the logs to ensure models loaded successfully.

3.  **Push to Registry:**
    ```bash
    docker push your-registry-username/flora-backend:latest
    ```

---

## ☁️ Step 3: Cloud Deployment

### Backend (Container Service)
Deploy the image you just pushed to your cloud provider (AWS App Runner, Google Cloud Run, Azure Container Apps).

*   **Image:** `your-registry-username/flora-backend:latest`
*   **Port:** `8000`
*   **Resources:** **Important!** Allocate at least **4GB RAM** and **2 vCPUs**. The LLM requires this memory to function.
*   **Environment Variables:**
    *   No special variables needed for models (they are baked in).
    *   Set `CORS_ORIGINS` if you want to restrict access to your frontend domain.

### Frontend (Vercel/Netlify)
1.  **Deploy the `frontend/` folder.**
2.  **Environment Variables:**
    You must tell the frontend where the backend lives.
    *   **Key:** `NEXT_PUBLIC_API_URL`
    *   **Value:** `https://your-backend-service.com` (Do not include a trailing slash)

---

### Monitoring (Prometheus & Grafana)
The `flora-backend` image **only** contains the Python application. It does **not** contain Prometheus or Grafana.

**Will the backend work without them?**
Yes, absolutely. The backend functions independently. You can deploy the backend now and add monitoring later.

**How to add them later?**
Since you cannot "bake" them into the backend image, you will deploy them as separate services in the same cloud environment.

1.  **Update Backend Code**: You will need to add a library like `prometheus-fastapi-instrumentator` to your `app.py` to expose a `/metrics` endpoint.
2.  **Deploy Prometheus**: Spin up a standard Prometheus container.
3.  **Networking**: Configure Prometheus to "scrape" (read data from) your backend's internal IP address on port 8000.
    *   *In Docker Compose*: It uses the service name `http://backend:8000`.
    *   *In Cloud (AWS/GCP)*: You put them in the same "Private Network" (VPC) and use the backend's internal service address.

## 🔒 Security & Git
*   The `backend/models/` folder is **ignored** by Git (`.gitignore`).
*   **Do not force add** model files to Git. They are too large and should only exist in the Docker image or local storage.

---

## 🆘 Troubleshooting
*   **"Volume not found"**: You are likely running an old `docker-compose` command that tries to mount `./models`. Use the built image instead.
*   **OOM (Out of Memory) Killed**: The container crashed because it ran out of RAM. Increase the memory allocation to 4GB+.
