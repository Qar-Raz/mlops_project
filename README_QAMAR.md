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

## 🎨 Frontend UI
Built with **Next.js** and **React**, featuring a modern, responsive chat interface with smooth animations.

*(Place UI screenshots here)*
<br>
<br>

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
## Architecture Diagram

<img width="4144" height="4932" alt="DIAGRAM 1" src="https://github.com/user-attachments/assets/2b0f234c-585e-4f56-9f82-d80cf74efd44" />

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


## 📈 Monitoring
<img width="1280" height="360" alt="image" src="https://github.com/user-attachments/assets/76d9e913-01ed-4195-b56e-818f72a2cdd3" />

<img width="1280" height="467" alt="image" src="https://github.com/user-attachments/assets/b381f598-912e-4eb7-a4de-0ec802f0d1fd" />

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

## 🛡️ Guardrails & Safety
We implement a multi-layered safety architecture to ensure responsible AI interactions. Our **LightweightGuard** system provides real-time validation for both user inputs and model outputs, focusing on high-performance filtering without the latency overhead of secondary LLM calls.

### Key Safety Layers
- **🚫 Content Moderation:** Optimized pattern matching to instantly block hate speech, violence, and self-harm content.
- **🔒 PII Protection:** Automated detection and redaction of sensitive information like email addresses and phone numbers (specifically optimized for regional formats).
- **🌿 Domain-Specific Context:** Custom-tuned filters that distinguish between botanical terms (e.g., "kill weeds", "shoot blight") and harmful language, ensuring accurate medical advice isn't flagged falsely.
- **⚡ Low-Latency Execution:** Designed for millisecond-level response times, running directly within the inference pipeline to maintain a smooth chat experience.
 
## D8: Security & Compliance
The project enforces strict security and governance standards. Compliance is addressed through clear documentation, including the presence of an **MIT License** in the root directory, which defines usage rights, and a **CODE\_OF\_CONDUCT.md** file, which guides ethical contributions.

For runtime security, we integrated mandatory dependency scanning into our CI/CD workflow. This process utilizes **`pip-audit`** to check all project dependencies for known vulnerabilities, with a critical policy that automatically fails the build and blocks deployment if any package contains a critical Common Vulnerability and Exposure (CVE).

#
