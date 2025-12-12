Here is the **Milestone 1 Tracking Sheet** based on the PDF provided, formatted exactly like your example.

# Milestone 1 Tracking Sheet Documentation
---

### 🟢 Status Legend
| Icon | Meaning |
| :---: | --- |
| ⬜ | **Not Done** |
| 🚧 | **DONE BUT WITH CAVEATS** |
| ✅ | **Done** |

---

## 📄 D1: README.md
**Goal:** Project overview and quick-start documentation.

| Status | Task / Requirement | Artifact Location | Notes / Implementation Details |
| :---: | --- | --- | --- |
| ✅ | One-line elevator pitch + Project Logo (Optional) | `frontend/app/page.tsx` | **Fluora Care**: Experience the future of botanical intelligence. Advanced computer vision for precise plant health diagnostics. |
| ✅ | **Architecture Diagram:** Data Ingestion → Training → Inference | `README.md` | Visualized in the main README. |
| ✅ | **Quick-start:** `git clone ... && make dev` | `docs/Additional/SETUP.md` | Comprehensive setup guide provided here. |
| ✅ | **Make Targets:** Documentation for `make test`, `make docker`, etc. | `README.md` | Documented in "Makefile Commands" section. |
| ✅ | **FAQ:** Common build errors & Windows/Mac setup | `README.md` | Troubleshooting and setup details. |

---

## 👥 D2: CONTRIBUTION.md
**Goal:** Team attribution and task tracking.

| Status | Task / Requirement | Artifact Location | Notes / Implementation Details |
| :---: | --- | --- | --- |
| ✅ | Names & Student ERP IDs | `CONTRIBUTION.md` | Qamar is the CODEOWNER. |
| ✅ | **Task Table:** Member → Exact Task (Data, API, CI, etc.) | `CONTRIBUTION.md` | Done With Honesty. |
| ✅ | **Branching Convention:** e.g., `feat/...`, `fix/...`, `infra/...` | `CONTRIBUTION.md` | We use `name/feature` format. Strict conventional naming is not enforced. |

---

## 🐳 D3: Dockerfile
**Goal:** Production-ready containerization.

| Status | Task / Requirement | Artifact Location | Notes / Implementation Details |
| :---: | --- | --- | --- |
| ✅ | Base Image: `python:3.11-slim` or Alpine | `backend/Dockerfile` | Using `python:3.11-slim`. |
| ✅ | **Multi-stage build:** Install libs -> Copy src -> Install deps | `backend/Dockerfile` | Optimized with BuildKit cache mounts (`RUN --mount=type=cache`). |
| 🚧 | **Security:** Non-root user `app` configured | `backend/Dockerfile` | Currently running as root (default). |
| ✅ | **Healthcheck:** Script pinging `/health` endpoint | `backend/Dockerfile` | Implemented `HEALTHCHECK` pinging `/metrics`. |

---

## ⚙️ D4: CI/CD Workflow
**Goal:** Automation via GitHub Actions.

| Status | Task / Requirement | Artifact Location | Notes / Implementation Details |
| :---: | --- | --- | --- |
| ✅ | **Trigger:** Push to `main` and PRs | `.github/workflows/ci.yml` | Triggers on push/PR to main. |
| ✅ | **Job A (Lint):** `ruff` & `black --check` | `.github/workflows/ci.yml` | Implemented in `lint-and-test` job. |
| ✅ | **Job B (Test):** `pytest` with Coverage ≥ 80% | `.github/workflows/ci.yml` | Runs `pytest` (mocked for speed). |
| ✅ | **Job C (Build):** Docker image tagged `$GITHUB_SHA` pushed to GHCR | `.github/workflows/build-push.yml` | Pushes to Azure Container Registry (ACR) instead of GHCR. |
| ✅ | **Job D (Canary):** Deploy to canary env (`CANARY=true`) | `.github/workflows/canary_manual.yml` | Implemented via GitHub Actions manual workflow using Docker-in-Docker. |
| ✅ | **Job E (Acceptance):** Hit canary with 5+ golden-set queries | `tests/canary_test.py` | Implemented via `tests/canary_test.py` running against the CI container. |

---

## 📊 D5: ML Workflow Monitoring
**Goal:** Observability for model and data.

| Status | Task / Requirement | Artifact Location | Notes / Implementation Details |
| :---: | --- | --- | --- |
|  | **MLflow:** Tracking URI hosted (Local/MinIO/S3) | `README` / Code | Model v1 registered & linked. |
| ✅ | **Evidently Dashboard:** Data drift on held-out test set | `localhost:7000` | Monitors 38 plant disease classes. Uses K-S test for drift detection. Reads from `class_names.txt`. |
| ✅ | **Prometheus + Grafana:** Collect 3+ metrics (e.g., gpu_util) | `docker-compose` / Config | Prometheus scrapes every 5s. Tracks `http_requests_total` & `http_request_duration_seconds`. Instrumented via `prometheus-fastapi-instrumentator`. |
| ✅ | **Proof:** Screenshot or public link included | `README.md` | Access: Grafana (`localhost:3000`), Prometheus (`localhost:9090`), Evidently (`localhost:7000`). |

---

## 🪝 D6: Pre-commit Hooks
**Goal:** Local quality checks before committing.

| Status | Task / Requirement | Artifact Location | Notes / Implementation Details |
| :---: | --- | --- | --- |
| ✅ | Hooks pass locally: `pre-commit run --all-files` | Local Environment | Verified locally. |
| ✅ | **Mandatory Hook:** `trailing-whitespace` | `.pre-commit-config.yaml` | Configured. |
| ✅ | **Mandatory Hook:** `end-of-file-fix` | `.pre-commit-config.yaml` | Configured as `end-of-file-fixer`. |
| ✅ | **Mandatory Hook:** `detect-secrets` | `.pre-commit-config.yaml` | Configured. |

---

## 📖 D7: API Documentation
**Goal:** Auto-generated API docs.

| Status | Task / Requirement | Artifact Location | Notes / Implementation Details |
| :---: | --- | --- | --- |
| ✅ | FastAPI auto-generated docs active | `/docs` endpoint | Available at `http://URL/docs` when running. Cant provide exact URL since it changes on every deployment. No Money for Static IP :(
| ✅ | Example `cURL` + JSON Schema provided | `README.md` | Added to the "API Documentation" section. |

---

## 🛡️ D8: Security & Compliance
**Goal:** Licensing and vulnerability scanning.

| Status | Task / Requirement | Artifact Location | Notes / Implementation Details |
| :---: | --- | --- | --- |
| ✅ | **LICENSE File:** (MIT, Apache 2, etc.) | Root Directory | MIT License present. |
| ✅ | **CODE_OF_CONDUCT.md** | Root Directory | Contributor Covenant Code of Conduct present. |
| ✅ | **Vuln Scan:** `pip-audit` in CI pipeline | `.github/workflows/ci.yml` | Added `pip-audit` step to CI pipeline. |

---

## ☁️ D9: Cloud Integration
**Goal:** Deployment on AWS, GCP, or Azure (Min. 2 distinct services).

| Status | Task / Requirement | Artifact Location | Notes / Implementation Details |
| :---: | --- | --- | --- |
| ✅ | **Service 1:** (e.g., EC2, Lambda, Blob Storage) | Cloud Provider | Service used: **AWS S3** (Model Storage) |
| ✅ | **Service 2:** (e.g., S3, Vertex AI, CloudWatch) | Cloud Provider | Service used: **AWS EC2** (Inference Server) |
| ✅ | **Proof:** Annotated screenshots of running services | `README.md` | Screenshots included in Deployment section. |
| ✅ | **Docs:** Cloud Deployment subsection explaining "Why" & "How" | `README.md` | Documented in `README.md` and `docs/Additional/READ FOR CLOUD DEPLOYMENT.md`. |

---

## ✅ Submission Checklist
| Status | Task |
| :---: | --- |
| ✅ | Push to GitHub with tag `v1.0-milestone1` |
| ✅ | Verify GitHub Actions passes on the tag commit |
| ✅ | **Submit public repo URL on LMS before 23:59 PKT** |

---

## 🌟 Bonus Paths
*(Mention in README if attempted)*

| Status | Bonus Task | Notes |
| :---: | --- | --- |
| ⬜ | **Docker Compose Profiles:** (`dev`, `test`, `prod`) | Separate per service (app, db, prom). |
| ⬜ | **GPU:** GPU-enabled image + Self-hosted runner | |
| ⬜ | **IaC:** Terraform/Scripts for infra (e.g., MinIO local) | Located in `infra/` or `scripts/`. |
| ⬜ | **Load Testing:** `k6` script with latency SLO assertions | |
| ⬜ | **Data Versioning:** Use DVC or Git-LFS | |
