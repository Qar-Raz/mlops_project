# Milestone 2 Tracking Sheet Documentation
---

### 🟢 Status Legend
| Icon | Meaning |
| :---: | --- |
| ⬜ | **To Do** |
| 🚧 | **DONE BUT WITH CAVEATS** |
| ✅ | **Done** | 

---

##  D1: Prompt Engineering Workflow
**More comprehensive Docs in docs/Prompt Report (M2_D1)**

| Status | Task / Requirement | Artifact Location | Notes / Implementation Details |
| :---: | --- | --- | --- |
| ✅ | Create folder structure | `experiments/prompts/` | File structured cleanup @Qamar |
| ✅ | **Strategy A:** Baseline (Zero-Shot) | `experiments/prompts/` | Avg ROUGE-L: 0.1296. |
| ✅ | **Strategy B:** Example-Driven (Few-Shot) <br>*(Test $k=3$ vs $k=5$)* | `experiments/prompts/` | **Winner.** Avg ROUGE-L: 0.2928. |
| ✅ | **Strategy C:** Advanced (CoT or Meta-Prompting) | `experiments/prompts/` | Avg ROUGE-L: 0.1368. |
| ✅ | Run Comparison on Held-out Dataset | `data/eval.jsonl` | 20 examples used. |
| ✅ | **Metric 1 (Quant):** Auto metric (ROUGE/BLEU/Cosine) | `mlruns/` | ROUGE-L used. |
| ✅ | **Metric 2 (Qual):** Human-in-the-loop rubric (1-5 scale) | `docs/Prompt Report (M2_D1).md` | Few-Shot scored 4.2/5. |
| ✅ | Log Metrics to W&B or MLflow | `mlruns/` | Parameters & metrics logged. NOTE THIS FOLDER IS NOT COMMIT AND IS KEPT ON S3, YOU CAN DOWNLOAD IT USING download_mlflow_logs_S3.py |
| ✅ | Create `prompt_report.md` | `docs/Prompt Report (M2_D1).md` | Includes indepth documentation of strategy structure, quantative /qualitative metrics results. |

---

##  D2: RAG Pipeline
**Goal:** Ingestion, Inference API, and Reproducibility.

| Status | Task / Requirement | Artifact Location | Notes / Implementation Details |
| :---: | --- | --- | --- |
| ✅ | Implement Ingestion Pipeline (FAISS/Chroma/LlamaIndex) | `backend/ingest.py` | |
| ✅ | Implement Inference API (FastAPI) | `backend/app.py` | |
| ✅ | **Diagram:** System Architecture (Ingestion/Retrieval/Gen) | `README.md, docs/RAG PIPELINE Document` | |
| ✅ | **Diagram:** Data Flow (Cloud/Local storage) | `README.md` | |
| ✅ | Create Makefile target (`make rag`) | `Makefile` | |

---

##  D3: Guardrails & Safety
**Goal:** Content filters and rule enforcement.

| Status | Task / Requirement | Artifact Location | Notes / Implementation Details |
| :---: | --- | --- | --- |
| ✅ | Implement Content Filters  | `backend/guard_utils.py` | |
| ✅ | **Rule 1:** Input Validation (e.g., PII, Injection) | `backend/guard_utils.py` | |
| ✅ | **Rule 2:** Output Moderation (e.g., Toxicity) | `backend/guard_utils.py` | |
| ✅ | Log Guardrail Events to Monitoring | `backend/guard_utils.py` | |
| ✅ | Document Integration | `docs/M2_D3(guardrails.md)` | |

---

##  D4: LLM Evaluation & Monitoring
**Goal:** Operational visibility and data drift.

| Status | Task / Requirement | Artifact Location | Notes / Implementation Details |
| :---: | --- | --- | --- |
| ✅ | Track Metrics via Prometheus | Prometheus Config | Prometheus configured to scrape LLM API metrics. Tracks request rates and latency. |
| ✅ | Visualize in Grafana | Grafana Dashboard | Dashboard operational at `localhost:3000`. Visualizes `http_requests_total` and response times. Query: `rate(http_requests_total[5m])`. |
| ✅ | **Monitor:** Latency, Token Usage, Cost, Violations | Dashboard | Monitoring endpoint `/metrics` exposed. Tracks request latency and total request count via Prometheus instrumentator. |
| ✅ | **Data Drift:** Evidently Dashboard for retrieval corpus | Dashboard | Dashboard at `localhost:7000`. Detects drift for 50% of features (1 out of 2). Monitors `class_id` and `confidence` distributions using K-S p-value test. |
| ✅ | Add Screenshots/Links to Dashboards | `README.md` | Screenshots included. Access: Grafana (`localhost:3000`), Evidently (`localhost:7000`), API docs available with `/metrics` endpoint for Prometheus scraping. |

---

## 🚀 D5: CI/CD for LLMOps
**Goal:** Automation and Testing (>80% Coverage).

| Status | Task / Requirement | Artifact Location | Notes / Implementation Details |
| :---: | --- | --- | --- |
| ✅ | **Step A:** Linting + Tests for prompt scripts | `.github/workflows/ci.yml` | Uses `ruff`, `black`, and mocked `pytest`. |
| ✅ | **Step B:** Automated Prompt Eval (Small dataset) | `.github/workflows/llm-ci.yml` | Runs `experiments/run_eval.py` on dispatch. |
| ✅ | **Step C:** Docker Build & Push (RAG API) | `.github/workflows/build-push.yml` | Pushes to Azure Container Registry (ACR). |
| 🚧 | **Step D:** Canary Deployment (LLM Service) | N/A | **DONE BUT WITH CAVEAT:** Skipped to avoid unnecessary compute costs and ACR credit consumption. |
| ✅ | Achieve **80% Code Coverage** (Unit + Integration) | `tests/` | Test cases in the mentioned folder. |

---

##  D6: Documentation & Reports
**Goal:** Finalize documentation.

| Status | Task / Requirement | Artifact Location | Notes / Implementation Details |
| :---: | --- | --- | --- |
| ✅ | **Update README:** Overview & Objectives | `README.md` | |
| ✅ | **Update README:** Diagrams & Dashboard Links | `README.md` | |
| ✅ | **Update README:** Step-by-step RAG Guide | `RMake File, docs/RAG pipleine Document.md` | |
| ✅ | **Update README:** API Usage Examples | `README.md` | |
| ✅ | Create Evaluation Report | `EVALUATION.md` | *Summarize methodology, prompt comparisons, insights.* |

---

##  D7: Cloud Integration (Required)
**Goal:** Use at least two cloud services (AWS, GCP, or Azure).

| Status | Task / Requirement | Artifact Location | Notes / Implementation Details |
| :---: | --- | --- | --- |
| ✅ | **Service 1:**  | Cloud Console | Service used: Amazon S3 |
| ✅ | **Service 2:** (e.g., EC2, Azure ML) | Cloud Console | Service used: Microsoft Azure |
| ✅ | Include Configuration Screenshots | `README.md` | |
| ✅ | Include Setup Steps | `README.md` | |

---

##  D8: Security & Compliance
**Goal:** Secure the pipeline.

| Status | Task / Requirement | Artifact Location | Notes / Implementation Details |
| :---: | --- | --- | --- |
| ✅ | Create Security Doc (Injection defenses, Privacy) | `SECURITY.md` | |
| ✅ | Run `pip-audit` in CI (Fail on Critical CVEs) | `ci.yml` | |
| ✅ | Document Responsible AI / Guardrails enforcement | `SECURITY.md` | |

---

## ✅ Submission Checklist
| Status | Task |
| :---: | --- |
| ✅ | Push to GitHub with tag `v2.0-milestone2` |
| ✅ | Ensure CI/CD workflow passes |
| ✅ | **Submit public repo URL on LMS before 23:59 PKT** |

---

## 🌟 Bonus Paths (+5 pts)
*(Mention in README if attempted)*

| Status | Bonus Task | Notes |
| :---: | --- | --- |
| ✅ | Implement LangChain/LlamaIndex toolchains | |
| ⬜ | Add A/B Testing Dashboard | |
| ⬜ | Deploy on Managed LLM Platform (Vertex/Azure AI Studio) | |
