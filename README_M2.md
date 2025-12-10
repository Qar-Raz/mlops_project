# 🌱 FloraCare

#### *Instant Diagnosis for Your Plants. Just an Image Away.*  

Experience the future of botanical intelligence. Advanced computer vision for precise plant health diagnostics.

## Introduction  
This repository contains Floracare, an LLMOps project dedicated to plant disease diagnosis. It is structured across two major milestones. Milestone 1 established the MLOps foundation, guaranteeing a reproducible system with complete Dockerization, CI/CD pipelines, and initial MLOps monitoring via a Prometheus/Grafana stack. Milestone 2 extended this foundation into the world of LLMOps, implementing a Retrieval-Augmented Generation (RAG) system for highly accurate inference. This final submission demonstrates best practices in LLM operations, including advanced prompt engineering workflows, robust AI guardrails for safety, and real-time operational monitoring of LLM latency, cost, and violations.

This README serves as the central documentation for our project, detailing the evolution from a machine learning repository (Milestone 1) to a full-fledged, operationalized LLMOps and RAG system (Milestone 2).

## File Structure

│   .gitignore  
│   .pre-commit-config.yaml  
│   CODE_OF_CONDUCT.md  
│   CONTRIBUTION.md  
│   docker-compose.yml  
│   Dockerfile  
│   EVALUATION.md  
│   LICENSE  
│   MakeFile  
│   Milestone1_Doc.md  
│   Milestone2_Doc.md  
│   prometheus.yml  
│   README.md  
│   requirements-dev.in  
│   requirements-dev.txt  
│   requirements.in  
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
 
## D5: ML Workflow Monitoring

## D6: Pre-commit Hooks

## D7: API Documentation

## D8: Security & Compliance

## D9: Cloud Integration


### MLOps & LLMOps  - Milestone 2  


This readme explains the M2 milestone, that focused on moving the project from initial planning into practical implementation. The work in M2 centered on building the core components of the system,
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



