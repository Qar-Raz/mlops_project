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
- **Milestone 1:** ✅ **9/9 Deliverables** | 🌟 **0/4 Bonus**
- **Milestone 2:** ✅ **8/8 Deliverables** | 🌟 **1/3 Bonus**

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

## 🏆 Why Our Project Excels


- **Fully Local & Private RAG (No APIs):** Unlike projects relying on paid APIs (OpenAI/GPT-4), we run a quantized **TinyLlama-1.1B** LLM and **ChromaDB** vector store entirely locally. This demonstrates advanced resource management and ensures complete data privacy.

- **Complex CV + NLP Pipeline:** We don't just serve a simple Scikit-learn model. We deploy a heavy **PyTorch** Computer Vision model alongside an LLM, integrating multiple deep learning modalities into a single inference engine.

- **Heavy Resource Management:** Our container is **5GB+** in size and requires **4GB+ RAM** to serve the CV and RAG models simultaneously. We deployed to **Azure** specifically because standard free-tier compute instances (often limited to 1GB RAM) were insufficient for this high-performance workload.

- **Production-Grade Frontend:** Moved beyond prototyping tools like Streamlit or Gradio. We built a responsive, animated **Next.js (React)** application with a polished chat interface, demonstrating full-stack engineering capabilities.

- **Custom-Built Knowledge Base:** We curated our own RAG corpus by scraping **322+ websites** covering all 38 plant disease classes, ensuring our chatbot provides domain-specific, accurate medical advice.

- **Dual CI/CD Pipelines:** Implemented specialized workflows:
    1.  **Frontend:** Instant deployments to **Vercel**.
    2.  **Backend:** Robust Docker build-and-push pipeline to **Azure Container Registry (ACR)**, handling heavy artifacts that exceed standard free-tier limits.


## File Structure
```
│   Dockerfile  
│   MakeFile  
│   Milestone1_Doc.md  
│   Milestone2_Doc.md  
│   prometheus.yml  
│   README.md  
│   requirements.txt  
│   SECURITY.md  
├───.github  
│   │   CODEOWNERS  
│   └───workflows  
├───backend  
│   └───scripts  
├───data  
├───docs    
├───experiments  
│   ├───prompts  
│   └───results  
├───frontend  
│   ├───app  
│   ├───components  
├───grafana  
│   ├───dashboards  
│   └───provisioning  
│       ├───dashboards  
│       └───datasources  
├───mlruns  
├───tests  
└───Web_Scrapping_For_Corpus  
```

---


### MLOps - Milestone 1  

## Architecture Diagram

<img width="4144" height="4932" alt="DIAGRAM 1" src="https://github.com/user-attachments/assets/2b0f234c-585e-4f56-9f82-d80cf74efd44" />

## Data Flow Diagram

<img width="2026" height="2581" alt="dataflow diagram" src="https://github.com/user-attachments/assets/8d484da1-42ba-4513-9d4e-c905a96e2661" />

## Architecture Overview

The application uses:
- **AWS S3** - For model storage and versioning
- **AWS EC2** - For hosting the prediction API
- **Docker** - For containerization
- **Uvicorn** - For serving the FastAPI application
- **Prometheus** - For scraping metrics and storing them in time-series DB
- **Grafana** - Connects to Prometheus as a data source
- **Evidently AI** - For monitoring data drift and model performance

---

## Quick Start
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

> **Note:** You'll know it's working if you see `(.venv)` at the start of your terminal prompt.

#### 3. Install All Dependencies

```bash
# Make sure your virtual environment is active!
pip install -r requirements.txt -r requirements-dev.txt
```

### 4. Activate Pre-Commit Hooks


```bash
pre-commit install
```
**You are now fully set up and ready to code!**

---

## Daily Development Workflow

1.  **Activate Environment:** Always start your work session by activating the virtual environment.
    ```bash
    source .venv/Scripts/activate
    ```2.  **Get Latest Changes & Create Branch:** Never work directly on `main`.
    ```bash
    git checkout main
    git pull origin main
    git checkout -b feat/your-descriptive-branch-name
    ```
3.  **Write Code!**
4.  **Commit Your Work:** Our pre-commit hooks will run automatically.
    ```bash
    git add .
    git commit -m "feat: your descriptive commit message"
    ```
    > **If your commit is stopped by the hooks:** It's usually because they automatically fixed a file. Just run `git add .` again and re-run your `git commit` command.

5.  **Push and Open a Pull Request:**
    ```bash
    git push origin feat/your-descriptive-branch-name
    ```
    Then, go to GitHub to open a Pull Request for review.

## Branch Naming Convention

For collaborative development on the our project, we adopted a clear, yet flexible, branching convention. We use name/feature format. Strict conventional naming is not enforced. Our structure ensures both contributor visibility and work item clarity by using the format `<name>/<type>/<description>`. All new work is integrated into the `main` branch via a Pull Request after successful CI checks.  

## Make Targets Reference

The `Makefile` is the primary interface for managing the entire project lifecycle, ensuring a reproducible workflow across development, testing, monitoring, and deployment.

| Target | Description | Milestone |
| :--- | :--- | :--- |
| `make dev` | Installs dependencies, activates the virtual environment, and starts the local FastAPI inference service. | M1, M2 |
| `make test` | Executes all unit and integration tests using `pytest` and verifies code coverage ($\ge80\%$ required for CI). | M1 |
| `make lint` | Runs code quality checks (`ruff` & `black --check`) to enforce code style. | M1 |
| `make format` | Automatically applies code formatting (`black`) and fixing (`ruff`) to all source files. | M1 |
| `make docker` | Builds the optimized, multi-stage, production-ready Docker image for the RAG API. | M1, M2 |
| `make audit` | Scans dependencies for known vulnerabilities using `pip-audit`. *(Critical CVEs fail CI)*. | M1, M2 |
| `make fetch-assets` | Downloads required model checkpoints and RAG document indices from remote cloud storage (e.g., S3/GCS). | M2 |
| `make rag` | **RAG Pipeline:** Executes the document ingestion/indexing pipeline to build the vector store. | M2 |

## FAQ - Common Issues and Solutions (In the end of Milestone 1)

## D3: DockerFile

The `Dockerfile` defines the production environment for our **Floracare** inference API, focusing on a balance of minimal size, fast builds, and essential dependencies. It is the core of our repeatable MLOps deployment.  

We use a layered build process to meet the following M1 requirements:

* **Slim Base Image:** Uses `python:3.11-slim` to maintain a small final image footprint.
* **Optimized Dependency Layers:** The build sequence is structured to maximize Docker caching. Critical steps like installing system dependencies (`cmake`, `build-essential`) and the large dependency, PyTorch (using the CPU-only wheel via `torch --index-url https://download.pytorch.org/whl/cpu`), are placed in early layers. This ensures these slower layers only rebuild if the base Python version changes, not every time application code or minor requirements are updated.
* **Minimalist System Packages:** Only the essential OS libraries required to build the Python dependencies are installed.
* **Application Execution:** The container exposes port `8000` and launches the FastAPI service using `CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]`.

## D4: CI/CD Workflows

#### **1. Trigger Conditions**

The CI workflow is configured to automatically run on two key events, ensuring continuous validation of all incoming code:

* **Push to `main`:** Immediately triggers a full build and test cycle, followed by the image build and push.
* **Pull Requests (PRs):** Triggers a lint and test run, providing early feedback to the developer before merging into `main`.

#### **2. Job A: Lint & Format**

This job enforces code consistency and quality, making the codebase maintainable and readable. It runs checks using:

* `black --check`: Verifies adherence to the Black code formatting style.
* `ruff`: A fast linter and formatter used for code quality and bug detection.

#### **3. Job B: Unit/Integration Test**

This is a critical job that runs the core test suite to validate application logic, data handling, and API endpoints.

* **Tool:** `pytest`
* **Requirement:** It uses the `--cov` flag to calculate code coverage, and the job fails if coverage falls below the required **$80\%$** threshold, enforcing rigorous testing standards.

#### **4. Job C: Docker Build & Push**

This job is responsible for creating and versioning the production artifact.

* **Containerization:** It uses the multi-stage `Dockerfile` to build the optimized RAG inference image.
* **Versioning:** The image is tagged with the specific Git commit SHA (`$GITHUB_SHA`) to guarantee traceability between the code, the artifact, and the deployed service.
* **Registry:** The final image is pushed to our designated **Azure Container Registry (ACR)**, making it available for deployment.

#### **5. Job D & E: Canary Deployment and Acceptance Testing**

These linked jobs ensure operational safety before promoting the image to the final production environment.

* **Canary Deployment:** This is a manual-trigger workflow, allowing a reviewer to initiate deployment to a segregated canary environment. This job uses a minimal Docker-in-Docker setup to pull the newly built image and run it with the `CANARY=true` environment flag.
* **Acceptance Test:** Immediately following a successful canary deployment, a dedicated test script runs. This script performs essential **smoke tests** and fires a suite of **golden-set queries** (known inputs/outputs) against the live, running canary service to verify:
    * The service is healthy (HTTP 200).
    * The RAG functionality is retrieving documents and generating correct, governed outputs.

#### 🔄 CI/CD Summary

##### Automated Testing Setup

- **GitHub Actions** - Automated testing workflow on push/pull requests
- **Pre-commit Hooks** - Code quality and linting checks
- **Integration Tests** - API endpoint validation tests
- **Unit Tests** - Model and utility function testing

##### Continuous Deployment Flow

1. **Local Development** → Developer makes changes and tests locally
2. **Git Push** → Code pushed to GitHub repository
3. **CI Pipeline** → Automated tests run via GitHub Actions
4. **EC2 Pull** → Pull latest changes on production server
5. **Auto-Reload** → Uvicorn automatically restarts with new code
6. **Health Check** → Automated verification of deployment success
7. **Monitoring** → Evidently dashboard tracks model performance
 
## D5: ML Workflow Monitoring

The primary objective was to establish a monitoring framework that provides visibility into:

- **Operational Health:** Throughput, latency, and error rates of the inference API.
- **Data Quality:** Detecting drift in the predicted plant disease classes relative to the training dataset.
- **System Reliability:** Ensuring the deep learning inference engine is responsive under load.

#### URLs
MLFlow: 
Grafana: http://localhost:3000  
Prometheus: http://localhost:9090  
Evidently: http://localhost:7000  

### Technology Stack

The solution uses Docker Compose to orchestrate four interconnected services:

| Component | Role | Integration Detail |
|-----------|------|-------------------|
| FastAPI Backend | Inference Engine | Serves the ResNet18 model and exposes the `/predict` endpoint. |
| Prometheus | Metrics Database | Scrapes performance metrics from the API container every 5 seconds. |
| Grafana | Visualization | Dashboards connected to Prometheus for real-time traffic analysis. |
| Evidently AI | Drift Detection | Customized script monitoring the 38 specific classes of the Plant Disease dataset. |  

### Dashboard Information

#### MLFlow
**Charts**  
<img width="1918" height="947" alt="image" src="https://github.com/user-attachments/assets/2568205b-ff24-4fd1-981c-ff90413acea6" />

<img width="1920" height="439" alt="image" src="https://github.com/user-attachments/assets/7e570e3b-3275-4f8d-9586-add758cdf61b" />

**Metrics**  
<img width="1920" height="955" alt="image" src="https://github.com/user-attachments/assets/618acf16-4fee-4ddb-8df4-09f71eebde38" />


#### Grafana
<img width="1280" height="658" alt="image" src="https://github.com/user-attachments/assets/553d4087-d600-4b88-b06f-c2cf02578243" />

####  Prometheus
Prometheus scrapes our app every 5s. app is the service name from Docker Compose, so Prometheus can reach it over the Compose network instead of localhost. This is how you're supposed to wire Prometheus ↔ FastAPI in Docker.

<img width="1280" height="656" alt="image" src="https://github.com/user-attachments/assets/de572ad1-49e0-4119-a124-d3ce2de856ed" />

#### Evidently

**Data Drift Detection**  

<img width="1578" alt="Drift Detection Overview" src="https://github.com/user-attachments/assets/ecbc3758-b8ab-4efa-a5b6-a88f98db4e41" />

This dashboard panel shows comprehensive drift detection across multiple features, comparing reference data with current production data.

**Feature Analysis and Distribution**  

<img width="1588" alt="Feature Analysis" src="https://github.com/user-attachments/assets/525bd3ac-5e4a-41d0-9ac6-1c2040dd52f5" />

Detailed analysis of individual feature distributions and their statistical properties over time.

**Data Quality Report**  

<img width="1564" alt="Data Quality Report" src="https://github.com/user-attachments/assets/464b66be-d589-4fb8-acb4-30e01f4f69d5" />

Comprehensive data quality metrics including missing values, data types, and consistency checks.

**Evidently AI Dashboard**  
<img width="1280" height="660" alt="image" src="https://github.com/user-attachments/assets/caedc215-181a-401a-ae13-e9d95288c63a" />

#### Summary of Monitoring Results

- ✅ **Drift Detection:** Real-time monitoring across all features with automated alerts
- ✅ **Data Quality:** No significant data quality issues detected in production
- ✅ **Performance Tracking:** Continuous model performance evaluation
- ✅ **Production Integration:** Connected with live model predictions for real-time analysis
- 🔄 **Automated Reports:** Regular reports generated for model health assessment

## D6: Pre-commit Hooks

* **Local Verification:** All team members have verified the hooks pass locally by running the command: `pre-commit run --all-files`. This ensures the checks function correctly on all local developer environments.
* **Mandatory Hook: Trailing Whitespace:** This is configured in `.pre-commit-config.yaml` to automatically remove unnecessary whitespace at the end of lines, promoting a clean and consistent code style.
* **Mandatory Hook: End-of-File Fixer:** Configured to ensure all files end with a consistent newline character, preventing cross-platform compatibility issues.
* **Mandatory Hook: Detect Secrets:** This hook actively scans the content of staged files for patterns that match common secrets (like API keys, tokens, and passwords) to prevent accidental leakage into the Git history.

## D7: API Documentation  

### Available Endpoints

#### Health Check
```http
GET /health
```
Returns server status. Use for monitoring and health checks.

#### Predict Plant Disease
```http
POST /predict
Content-Type: multipart/form-data
```
Upload a plant leaf image and receive real-time disease classification with confidence scores.

Available at http://URL/docs when running. Cant provide exact URL since it changes on every deployment.  

<img width="1362" height="686" alt="image" src="https://github.com/user-attachments/assets/10c70623-0628-42aa-909b-1c753d397235" />
 
## D8: Security & Compliance
The project enforces strict security and governance standards. Compliance is addressed through clear documentation, including the presence of an **MIT License** in the root directory, which defines usage rights, and a **CODE\_OF\_CONDUCT.md** file, which guides ethical contributions.

For runtime security, we integrated mandatory dependency scanning into our CI/CD workflow. This process utilizes **`pip-audit`** to check all project dependencies for known vulnerabilities, with a critical policy that automatically fails the build and blocks deployment if any package contains a critical Common Vulnerability and Exposure (CVE).

## D9: 
For our cloud environment, we opted to use two distinct services from Microsoft Azure. We initially attempted deployment on **AWS EC2**, but encountered performance and resource constraints due to the limited 1GB of storage space available for the RAG assets. We successfully switched our architecture to Azure to ensure stability and proper scaling.

The core services used are:

1.  **Azure Container Instances (ACI):** Used to host the finalized RAG inference API (the Docker image built in D4). This service provides quick, containerized hosting without the overhead of managing a full virtual machine (VM).
2.  **Azure Blob Storage:** Used as the persistent, scalable backend storage for large model checkpoints and the pre-indexed RAG vector store.

This setup ensures a decoupled ML workflow: the inference API (ACI) pulls required assets (models, RAG index) from the secure and scalable Blob Storage during its startup phase. For a guide on the setup, provisioning, and configuration steps, please refer to `docs/M1_D5.md`.

---

## Troubleshooting Guide

### Common Issues and Solutions

#### Issue 1: Connection Refused on Port 8000

**Symptoms:** Cannot access API endpoint from browser

**Solutions:**
```bash
# Check if security group allows inbound traffic on port 8000
aws ec2 describe-security-groups --group-ids sg-xxxxx

# Verify application is running
ps aux | grep uvicorn

# Check if port is listening
netstat -tulpn | grep 8000
```

---

#### Issue 2: Model Not Loading from S3

**Symptoms:** Application starts but predictions fail

**Solutions:**
```bash
# Verify IAM role has S3 access
aws sts get-caller-identity

# Check if model file exists in S3
aws s3 ls s3://mlopsmodel/

# Test S3 download manually
aws s3 cp s3://mlopsmodel/model.pkl /tmp/test.pkl
```

---

#### Issue 3: 502 Bad Gateway Error

**Symptoms:** Nginx/Load Balancer returns 502

**Solutions:**
```bash
# Check application logs
tail -f /var/log/uvicorn.log

# Restart the application
pkill -f uvicorn
python -m uvicorn src.app.main:app --host 0.0.0.0 --port 8000 --reload

# Check system resources
top
df -h
```

---

#### Issue 4: Auto-Reload Not Working

**Symptoms:** Code changes not reflected after git pull

**Solutions:**
```bash
# Ensure --reload flag is used
python -m uvicorn src.app.main:app --host 0.0.0.0 --port 8000 --reload

# Check file permissions
ls -la MLOPS_PROJECT/

# Manually restart if needed
pkill -f uvicorn
```

---

### MLOps & LLMOps  - Milestone 2  

This portion of the README explains the M2 milestone, that focused on moving the project from initial planning into practical implementation. The work in M2 centered on building the core components of the system,
refining the data pipeline, running structured experiments, and establishing the monitoring and testing setup needed for reliable performance.

## LLMOps Objectives
- Compare multiple prompt strategies on a curated evaluation dataset.  
- Implement a **Retrieval-Augmented Generation (RAG)** workflow with ingestion & inference pipelines.  
- Integrate monitoring, evaluation, and safety guardrails into the LLM pipeline.  
- Document, containerize, and automate everything through CI/CD.

## D1 — Prompt Engineering Workflow


## D2 — RAG (Retrieval-Augmented Generation) Pipeline

## D3 — Guardrails & Safety Mechanisms

## D4 — LLM Evaluation & Monitoring

## D5 — CI/CD for LLMOps

## D6 — Documentation & Reports

## D7 — Cloud Integration (Required)

## D8 — Security & Compliance



