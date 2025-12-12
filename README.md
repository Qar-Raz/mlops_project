# 🌿 Fluora Care
> **Experience the future of botanical intelligence.**
> Advanced computer vision for precise plant health diagnostics.

**Fluora Care** is a robust, end-to-end MLOps solution designed to revolutionize plant health management. It seamlessly integrates a **Computer Vision** model for instant disease detection with a **RAG-powered LLM Chatbot** to provide actionable treatment advice.

Built on a modern **Microservices Architecture**, the system features:
*   **Frontend:** A responsive **Next.js** application deployed on **Vercel**.
*   **Backend:** High-performance **FastAPI** inference engine serving PyTorch & ONNX models.
*   **Infrastructure:** Containerized with Docker and hosted via **Azure Container Registry (ACR)**.
*   **Monitoring:** Comprehensive monitoring using **Prometheus** & **Grafana** for system metrics, and **Evidently AI** for ML data drift detection.

## 📊 Project Status
- **Milestone 1:** ✅ **9/9 Deliverables** |
- **Milestone 2:** ✅ **8/8 Deliverables** |

## 🔗 Quick Links
- **🎥 [Website Demo](https://drive.google.com/drive/folders/1cJMO7OChqmSsNk4tK0FmxPzJXJ2AmudD?usp=drive_link)**
- **🌐 [Website Deployment](https://mlops-project-five.vercel.app/)**
  > *⚠️ Note: The backend API container is currently offline to conserve cloud credits. If the app does not respond, please refer to the demo video.*
- **📋 [Milestone 1 Checklist](./Milestone1_Doc.md)**
- **📋 [Milestone 2 Checklist](./Milestone2_Doc.md)**
- **📂 [Detailed Deliverables Documentation](./docs/)**
  > *Note: Detailed documentation is provided for advanced deliverables. Simpler tasks are documented directly in the checklists.*
- **💻 [Frontend Source (Next.js)](./frontend/)**
- **⚙️ [Backend Source (FastAPI)](./backend/)**
- **🧪 [Test Suite](./tests/)**
  > *Tests are automatically executed in the CI pipeline.*
- **🔬 [Experiments & Evaluation](./experiments/)**
   > *For evaluation of LLM, prompt report*
- **✨ [Bonus: LangChain & Custom Retrievers](./docs/M2_Bonus_LangChainLLama.md)**

## 🏆 Why Our Project Excels


- **Fully Local & Private RAG (No APIs):** Unlike projects relying on paid APIs (OpenAI/GPT-4), we run a quantized **TinyLlama-1.1B** LLM and **ChromaDB** vector store entirely locally. This demonstrates advanced resource management and ensures complete data privacy.

- **Complex CV + NLP Pipeline:** We don't just serve a simple Scikit-learn model. We deploy a heavy **PyTorch** Computer Vision model alongside an LLM, integrating multiple deep learning modalities into a single inference engine.

- **Heavy Resource Management:** Our container is **5GB+** in size and requires **4GB+ RAM** to serve the CV and RAG models simultaneously. We deployed to **Azure** specifically because standard free-tier compute instances (often limited to 1GB RAM) were insufficient for this high-performance workload.

- **Production-Grade Frontend:** Moved beyond prototyping tools like Streamlit or Gradio. We built a responsive, animated **Next.js (React)** application with a polished chat interface, demonstrating full-stack engineering capabilities.

- **Custom-Built Knowledge Base:** We curated our own RAG corpus by scraping **322+ websites** covering all 38 plant disease classes, ensuring our chatbot provides domain-specific, accurate medical advice.

- **Dual CI/CD Pipelines:** Implemented specialized workflows:
    1.  **Frontend:** Instant deployments to **Vercel**.
    2.  **Backend:** Robust Docker build-and-push pipeline to **Azure Container Registry (ACR)**, handling heavy artifacts that exceed standard free-tier limits.

## 💻 Local Setup Guide

Follow these steps to run the entire application (Backend + Frontend) locally on your machine.

### 1. Backend Setup (Docker)
Ensure Docker Desktop is installed and running.

```bash
# Build and start the backend services (API, Prometheus, Grafana)
docker-compose up --build
```
*The backend API will be available at `http://localhost:8000`.*

### 2. Frontend Setup (Next.js)
Open a new terminal window.

```bash
# Navigate to the frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```
*The frontend will be available at `http://localhost:3001`.*

### 3. Environment Configuration
For optimal local performance, ensure your frontend is pointing to your local backend.

1.  Open `frontend/.env.local`.
2.  Update the variables to use the local proxy:

```dotenv
# frontend/.env.local
NEXT_PUBLIC_API_URL=/api/proxy
BACKEND_URL=http://127.0.0.1:8000
```
*This configuration routes requests through the Next.js proxy (avoiding CORS) and points them to your local Docker container.*

## Quick Start for Development
#### 1. Clone the Repository
```bash
git clone https://github.com/Qar-Raz/MLOPS_Project.git
```

#### 2. Create & Activate Virtual Environment
This isolates our project's dependencies from your system.

```bash
# Create the virtual environment
python -m venv .venv

# Activate the environment (choose the command for your OS)

# macOS / Linux
source .venv/bin/activate

# Windows (Git Bash)
source .venv/Scripts/activate
```


## 🛠️ Makefile Commands
For convenience, we provide a `Makefile` to automate the RAG pipeline. 

**IMPORTANT NOTE : WE OPTED FOR CONTAINER BUILD OVER MAKEFILES SO READ LOCAL SETUP GUIDE FOR COMPLETE LOCAL DEPLOYMENT** 

```bash
# Install dependencies
make install

# Run the full RAG pipeline
make rag

# Run the backend API locally
make run-app

# Clean up cache and artifacts
make clean
```

## 🎨 Frontend UI
Built with **Next.js** and **React**, featuring a modern, responsive chat interface with smooth animations.

The following shows the Vercel Dashboard:
<img width="1909" height="1002" alt="image" src="https://github.com/user-attachments/assets/22cfa87a-e9b4-4c2d-8d1c-7342fb92271d" />

Main UI Images
<img width="1919" height="1199" alt="image" src="https://github.com/user-attachments/assets/9789a77c-f29c-4b0e-bca9-d8253673c6f6" />
<img width="1919" height="1199" alt="image" src="https://github.com/user-attachments/assets/a28614db-a542-4f08-b7e8-bd76c677782e" />
<img width="1912" height="998" alt="image" src="https://github.com/user-attachments/assets/e640ec68-aa78-4e27-9868-c906055ce1d8" />



## 🏗️ Architecture Overview
The system follows a microservices architecture, integrating multiple components for a seamless user experience.

<img width="2026" height="2581" alt="dataflow diagram" src="https://github.com/user-attachments/assets/8d484da1-42ba-4513-9d4e-c905a96e2661" />
### Microservices Summary
- **Frontend (Next.js):** Handles user interaction, image uploads, and chat interface.
- **Backend (FastAPI):** Orchestrates the ML pipeline, serving both the CV model and the RAG chatbot.
- **Model Registry (S3/Local):** Stores versioned model artifacts (ONNX, GGUF, ChromaDB).
- **Monitoring Stack:**
    - **Prometheus:** Scrapes system and application metrics.
    - **Grafana:** Visualizes real-time performance dashboards.
    - **Evidently AI:** Tracks data drift and model quality.
- **Infrastructure:** Dockerized services orchestrated via Docker Compose (local) or Azure Container Instances (cloud).

## 📂 Dataset
We utilized a comprehensive dataset covering 38 distinct plant disease classes.
- **Dataset Link:** [Plant Village Dataset](https://www.kaggle.com/datasets/abdallahalidev/plantvillage-dataset)

For Corpus, we webscrapped 322 sites for all relevant plant information. More information in `Web_Scrapping_For_Corpus`

## 🧠 Model Training & RAG Pipeline
Our system combines state-of-the-art Computer Vision with a custom Retrieval-Augmented Generation (RAG) pipeline.

## Complete Model Architecture Diagram (RAG + CV + Monitoring)

<img width="4144" height="4932" alt="DIAGRAM 1" src="https://github.com/user-attachments/assets/2b0f234c-585e-4f56-9f82-d80cf74efd44" />


### 🔄 ML Workflow & Service Interaction
The system integrates multiple MLOps services to ensure a robust lifecycle from data to inference.

1.  **Data Ingestion:**
    *   **CV Data:** PlantVillage dataset is loaded and augmented (random crops, flips) using `torchvision`.
    *   **RAG Data:** Scraped agricultural text is chunked and embedded using `sentence-transformers`.
2.  **Training & Tracking (MLflow):**
    *   **CV Model:** The Swin Transformer training is tracked via **MLflow** (hosted locally on port 5000). It logs hyperparameters (learning rate, batch size), metrics (loss, accuracy), and artifacts (ONNX models).
    *   **RAG Pipeline:** Ingestion parameters and vector store statistics are also logged to MLflow for reproducibility.
3.  **Inference:**
    *   The **FastAPI** backend loads the optimized ONNX model and ChromaDB vector store.
    *   **Prometheus** scrapes real-time inference metrics (latency, request count) from the API.
    *   **Evidently AI** monitors the input data for drift against the training baseline.

### 1. Computer Vision Model for Plant Diseases
We trained a **Swin Transformer** (`microsoft/swin-tiny-patch4-window7-224`) on the **PlantVillage** dataset to classify 38 distinct plant disease classes.
- **Framework:** Hugging Face Transformers & PyTorch
- **Training Strategy:**
    - **Augmentation:** Random resized crops, horizontal flips, 15° rotations, and color jitter.
    - **Optimization:** AdamW optimizer with a learning rate of `2e-5` and batch size of 32.
    - **Tracking:** Full experiment tracking via **MLflow** (loss, accuracy, artifacts).
- **Performance:** Achieved high accuracy on the validation set with Early Stopping (patience=3).

### 2. RAG Pipeline (Knowledge Retrieval)
We built a hybrid retrieval system to ground LLM responses in factual agricultural data.
- **Ingestion:**
    - **Source:** Custom JSON dataset scraped from 322+ agricultural websites.
    - **Chunking:** `RecursiveCharacterTextSplitter` (Chunk size: 800, Overlap: 100).
    - **Embeddings:** `sentence-transformers/all-MiniLM-L6-v2`.
- **Vector Store:** **ChromaDB** (Persistent local storage).
- **Hybrid Retrieval:**
    - Combines **BM25 (Sparse)** for exact keyword matching (weight: 0.4).
    - Combines **Chroma (Dense)** for semantic search (weight: 0.6).
    - **Ensemble Retriever:** Merges results to ensure both specific terminology and general context are captured.
 
 ### 🛠️ Step-by-Step RAG Deployment Guide
To deploy the RAG pipeline locally, follow these steps:

1.  **Prepare the Corpus:**
    Ensure your scraped data is in `Web_Scrapping_For_Corpus/sample.json`.
2.  **Run Ingestion:**
    Execute the ingestion script to chunk text and build the ChromaDB vector store.
    ```bash
    python backend/ingest.py
    ```
    *This creates the `backend/models/flora_rag_db` directory.*
3.  **Verify Database:**
    Check that the vector store is populated.
    ```bash
    ls backend/models/flora_rag_db
    ```
4.  **Start the API:**
    Launch the FastAPI server which loads the RAG retriever.
    ```bash
    uvicorn backend.app:app --reload
    ```

## 🧪 MLflow Experiment Tracking
We use **MLflow** to track all experiments locally.

**Launch the Dashboard:**
```bash
# View Model Training Experiments (Port 5000)
mlflow ui --backend-store-uri ./mlruns/mlruns_training --port 5000
```
*Access at: `http://localhost:5000`*

**Service Interaction:**
*   **Training Scripts:** `pipeline.py` logs metrics directly to the local MLflow tracking URI.
*   **Artifact Store:** Models and vector stores are saved as artifacts within MLflow runs for version control.
*   **Comparison:** We use the MLflow UI to compare different prompt strategies (Zero-shot vs Few-shot) and CV model checkpoints.


## 📈 Monitoring (Prometheus and Grafana + Evidently AI
Grafana Landing Page:
<img width="1919" height="1003" alt="image" src="https://github.com/user-attachments/assets/aedbf663-1650-4227-a02b-8fdbf9eff8d5" />

Grafana Dashboard with System Information (Milestone 1)
<img width="1422" height="531" alt="image" src="https://github.com/user-attachments/assets/40444dd8-9a89-49e5-b4da-181d6aeac884" />


Grafana Dashboard with Guardrails and Token Information (Milestone 2)
<img width="1280" height="360" alt="image" src="https://github.com/user-attachments/assets/76d9e913-01ed-4195-b56e-818f72a2cdd3" />

<img width="1280" height="467" alt="image" src="https://github.com/user-attachments/assets/b381f598-912e-4eb7-a4de-0ec802f0d1fd" />

Prometheus Landing Page
<img width="1915" height="1025" alt="image" src="https://github.com/user-attachments/assets/12584bfa-c899-427f-a945-4d71d0fd95e3" />



## LLM Evaluation & Monitoring Using MLflow

#### MLFlow
The following figure displays the comprehensive list of metrics recorded at the conclusion of the 10th epoch:
<img width="1920" height="955" alt="Screenshot 2025-12-06 at 3 58 27 PM" src="https://github.com/user-attachments/assets/4046fb73-f8b4-4cd9-ad01-36728a9fdfa4" />

These Figure shows the metrics for CV model 
<img width="1918" height="947" alt="image" src="https://github.com/user-attachments/assets/2568205b-ff24-4fd1-981c-ff90413acea6" />

<img width="1920" height="439" alt="image" src="https://github.com/user-attachments/assets/7e570e3b-3275-4f8d-9586-add758cdf61b" />

**Metrics**  
<img width="1920" height="955" alt="image" src="https://github.com/user-attachments/assets/618acf16-4fee-4ddb-8df4-09f71eebde38" />

**Training Dynamics and Visualization Analysis**

The following figures illustrate the progression of key metrics over the course of the training steps.  
These visualizations provide insight into the learning schedule, convergence behavior, and system performance.

<img width="1918" height="947" alt="Screenshot 2025-12-06 at 3 57 50 PM" src="https://github.com/user-attachments/assets/89fc92aa-b800-47d0-8fb4-6aad4193a86f" />

<img width="1920" height="439" alt="Screenshot 2025-12-06 at 3 58 09 PM" src="https://github.com/user-attachments/assets/53d5374d-59f2-4aa7-bdd6-12df1f11ffb4" />

#### Evidently Dashboard:
<img width="1280" height="720" alt="image" src="https://github.com/user-attachments/assets/df3c7089-f581-4226-a263-58266aba14b7" />

<img width="511" height="161" alt="image" src="https://github.com/user-attachments/assets/eb842224-1917-4169-a85c-084df59dc2a8" />

## ☁️ Cloud Deployment
## Cloud Integration

### Azure Deployment

<img width="1280" height="600" alt="image" src="https://github.com/user-attachments/assets/5283af76-d528-46bd-8ca3-85b7b8bfa87e" />


<img width="1163" height="480" alt="image" src="https://github.com/user-attachments/assets/c5fbceda-cbe7-46bc-8ed3-a36c784c68b6" />  

### 🔧 Deployment Steps

#### 1. AWS S3 Setup

##### Creating S3 Bucket

Created an S3 bucket named `mlopsmodel` in the `eu-north-1` region to store the trained model artifacts for version control and easy access.

<img width="1568" height="306" alt="image" src="https://github.com/user-attachments/assets/f9acd689-5bf7-4b11-86e7-acbbfa39abbc" />

**Bucket Details:**
- **Name:** mlopsmodel
- **Region:** Europe (Stockholm) eu-north-1
- **Creation Date:** October 31, 2025, 01:41:30 (UTC+05:00)

## 🔄 CI/CD Workflows
We utilize GitHub Actions for a robust, automated development lifecycle.

| Workflow | File | Trigger | Description |
| :--- | :--- | :--- | :--- |
| **CI Pipeline** | `ci.yml` | Push/PR to `main` | Runs linting (Ruff/Black), unit tests (Pytest), and security scans (pip-audit). |
| **Build & Push** | `build-push.yml` | Push to `main` | Builds the backend Docker image and pushes it to Azure Container Registry (ACR). |
| **LLM Evaluation** | `llm-ci.yml` | Manual / Schedule | Runs prompt engineering experiments and evaluates LLM performance using Evidently AI. |
| **Canary Test** | `canary_manual.yml` | Manual | Deploys a lightweight container instance to verify system health before full rollout. |

Images of the workflows GitHub actions page are attached to demonstrate that the final run was successful 
<img width="1907" height="835" alt="image" src="https://github.com/user-attachments/assets/5d15a3ce-8395-4f69-b255-a4aebfe1bb30" />
<img width="1918" height="848" alt="image" src="https://github.com/user-attachments/assets/2d81fe79-2b58-4a54-9232-38c28fa4f35d" />
<img width="1914" height="843" alt="image" src="https://github.com/user-attachments/assets/7b25ae15-cb9d-4a1c-8a31-2ec7ef8dfe76" />
<img width="1915" height="848" alt="image" src="https://github.com/user-attachments/assets/bb878ad0-7bec-4ca9-859e-ba8312ecc07a" />




## 🛡️ Guardrails & Safety
We implement a multi-layered safety architecture to ensure responsible AI interactions. Our **LightweightGuard** system provides real-time validation for both user inputs and model outputs, focusing on high-performance filtering without the latency overhead of secondary LLM calls.

### Key Safety Layers
- **🚫 Content Moderation:** Optimized pattern matching to instantly block hate speech, violence, and self-harm content.
- **🔒 PII Protection:** Automated detection and redaction of sensitive information like email addresses and phone numbers (specifically optimized for regional formats).
- **🌿 Domain-Specific Context:** Custom-tuned filters that distinguish between botanical terms (e.g., "kill weeds", "shoot blight") and harmful language, ensuring accurate medical advice isn't flagged falsely.
- **⚡ Low-Latency Execution:** Designed for millisecond-level response times, running directly within the inference pipeline to maintain a smooth chat experience.

- We implement a multi-layered safety architecture to ensure responsible AI interactions. Our **LightweightGuard** system provides real-time validation for both user inputs and model outputs.

**📄 [Read the full Guardrails Documentation](./docs/guardrails.md)**
## 📖 API Documentation
The backend exposes a RESTful API via FastAPI. Below are the core endpoints.

### 1. Predict Disease (CV + RAG)
Upload a plant leaf image to get a diagnosis and treatment plan.

**Endpoint:** `POST /predict`

```bash
curl -X POST "http://localhost:8000/predict" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@/path/to/leaf_image.jpg"
```

**Response:**
```json
{
  "diagnosis": "Apple___Black_rot",
  "confidence": "98.5%",
  "explanation": "Black rot is a fungal disease... [LLM Generated Advice]",
  "chat_context": "..."
}
```

### 2. Chat with Expert (LLM)
Ask follow-up questions based on the diagnosis context.

**Endpoint:** `POST /chat`

```bash
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{
           "question": "What fungicides should I use?",
           "context": "Black rot is caused by..."
         }'
```

**Response:**
```json
{
  "answer": "For Black rot, effective fungicides include Captan and Myclobutanil..."
}
```

### 3. System Metrics (Prometheus)
Get real-time system performance and drift metrics.

**Endpoint:** `GET /metrics`

```bash
curl -X GET "http://localhost:8000/metrics"
```

### 🛡️ Vulnerability Scanning
For runtime security, we integrated mandatory dependency scanning into our CI/CD workflow. This process utilizes **`pip-audit`** to check all project dependencies for known vulnerabilities.
Furthermore, we also ran npm audit for frontend dependencies.

**Run Locally:**
```bash
pip install pip-audit
pip-audit

cd frontend
npm audit
```

**Scan Results: pip audit**
<img width="239" height="428" alt="image" src="https://github.com/user-attachments/assets/1dde60cd-6f05-4cb5-8a7e-e435d7dacebf" />

<br>

The pipeline is configured to fail builds if critical CVEs are detected, ensuring no vulnerable code reaches production.


**Scan Results: npm audit**
<img width="745" height="332" alt="image" src="https://github.com/user-attachments/assets/e66c4e44-69cb-4639-ad7d-f6b2453d5ef4" />


## ❓ FAQ & Troubleshooting

### General Questions
**Q: What is the primary goal of Fluora Care?**
> **A:** To provide an offline-capable, privacy-focused tool for farmers to diagnose plant diseases using computer vision and receive treatment advice via a specialized chatbot.

**Q: Why use a local LLM (TinyLlama) instead of OpenAI?**
> **A:** We prioritize data privacy and cost-efficiency. Running locally ensures no sensitive agricultural data leaves the device and eliminates API usage fees.

**Q: Is an internet connection required?**
> **A:** No. Once the Docker container is built and models are downloaded, the entire inference pipeline (CV + Chat) runs completely offline.

### Technical Troubleshooting

**Q: The Docker container exits immediately with code 137?**
> **A:** This usually means Out Of Memory (OOM). Ensure your Docker Desktop has at least **4GB RAM** allocated.

**Q: I see "ONNX Model missing" in the logs?**
> **A:** You need to download the model artifacts. Run `python backend/download_models.py` (if available) or ensure `backend/models/flora_cv_onnx/` contains `model.onnx`.

**Q: How do I run this on Windows?**
> **A:** We recommend using **WSL2** or **Git Bash**. The `Makefile` commands might need adjustment for PowerShell.
 
#
