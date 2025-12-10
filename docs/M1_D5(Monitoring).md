# Milestone 1 Report: ML Workflow Monitoring & Observability

**Project:** Plant Disease Detection MLOps  
**Deliverable:** D5 - ML Workflow Monitoring  

---

## 1. Executive Summary

This report details the implementation of a production-grade monitoring infrastructure for the Plant Disease Detection System. The solution orchestrates Evidently AI, Prometheus, and Grafana within a containerized environment to ensure the observability of the deep learning model. The system is fully integrated into the CI/CD pipeline, ensuring that the heavy PyTorch ResNet18 model can be deployed and monitored reliably.

---

## 2. Objective

The primary objective was to satisfy Requirement D5 by establishing a monitoring framework that provides visibility into:

- **Operational Health:** Throughput, latency, and error rates of the inference API.
- **Data Quality:** Detecting drift in the predicted plant disease classes relative to the training dataset.
- **System Reliability:** Ensuring the deep learning inference engine is responsive under load.

---

## 3. Technology Stack

The solution uses Docker Compose to orchestrate four interconnected services:

| Component | Role | Integration Detail |
|-----------|------|-------------------|
| FastAPI Backend | Inference Engine | Serves the ResNet18 model and exposes the `/predict` endpoint. |
| Prometheus | Metrics Database | Scrapes performance metrics from the API container every 5 seconds. |
| Grafana | Visualization | Dashboards connected to Prometheus for real-time traffic analysis. |
| Evidently AI | Drift Detection | Customized script monitoring the 38 specific classes of the Plant Disease dataset. |

---

## 4. Implementation Details

### 4.1 Operational Monitoring (Prometheus & Grafana)

To monitor the heavy inference workload, we implemented the Middleware Pattern in the backend.

#### 4.1.1 Instrumentation

We integrated `prometheus-fastapi-instrumentator` into the main application logic (`backend/app.py`). This automatically captures the latency of the ResNet18 model during inference.

```python
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()

# Middleware to capture metrics for the Plant Disease Model
instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app)
```

#### 4.1.2 Visualization

Grafana is configured with a persistent datasource to visualize:

- `http_requests_total`: The volume of leaf images being processed.
- `http_request_duration_seconds`: The time taken by the PyTorch model to return a prediction.

### 4.2 Data Quality Monitoring (Evidently AI)

#### 4.2.1 Dataset Integration

The monitoring system is tightly coupled with the project's domain. The data drift detection script dynamically reads the `class_names.txt` file—which contains the 38 specific labels from the New Plant Diseases Dataset—to ensure the report reflects the actual model outputs.

#### 4.2.2 Drift Logic

The system generates a report comparing:

- **Reference Distribution:** The baseline distribution of disease classes from the training set.
- **Current Distribution:** The live predictions coming from the production model.
- **Statistical Test:** Uses the Kolmogorov-Smirnov (K-S) test to detect if specific diseases (e.g., `Apple___Black_rot`) are trending abnormally.

```python
# Loading the actual project classes
with open("class_names.txt", "r") as f:
    class_names = [line.strip() for line in f.readlines()]

# Generate Data Drift Report based on these specific classes
report = Report(metrics=[DataDriftPreset()])
report.run(reference_data=reference_data, current_data=current_data)
```

### 4.3 CI/CD & Optimization (Technical Challenges Solved)

Deploying heavy Deep Learning models in a CI/CD environment (GitHub Actions) presents significant challenges regarding disk space and dependency management.

#### 4.3.1 Disk Space Optimization (ENOSPC Fix)

**Challenge:** The standard PyTorch installation includes NVIDIA CUDA drivers (~4GB), which caused the GitHub Runner to run out of space.

**Solution:** We configured `requirements.txt` to strictly use the CPU-optimized version of PyTorch.

**Result:** Reduced build size by ~2.5GB, allowing the full ResNet18 pipeline to pass CI checks.

```text
--extra-index-url https://download.pytorch.org/whl/cpu
torch==2.2.0+cpu
```

#### 4.3.2 Version Compatibility

We resolved critical conflicts between the latest numpy release (v2.0) and the monitoring libraries by pinning stable versions (`evidently==0.4.0`, `numpy<2`) to ensure a robust build.

---

## 5. Results

The implementation successfully provides a 360-degree view of the ML system.

- ✅ **Prometheus:** Validated that metrics are being scraped from the API container.
- ✅ **Grafana:** Dashboard operational, visualizing real-time inference traffic.
- ✅ **Evidently:** Report generated successfully, validating distribution shifts across the 38 plant disease classes.

---

## 6. Reproduction Instructions

To spin up the full stack locally:

### Step 1: Build the Infrastructure
```bash
docker-compose up --build
```

### Step 2: Access Dashboards
- **Grafana:** http://localhost:3000
- **Prometheus:** http://localhost:9090
- **Evidently:** http://localhost:7000

---

#### Health Check Endpoint

```python
@app.get("/health")
async def health_check():
    return {"status": "ok"}
```

#### Connecting FastAPI with Grafana
##### How Grafana is run
Grafana is defined as a service in `docker-compose.yml`:
```yaml
grafana:
  image: grafana/grafana:latest
  container_name: grafana
  environment:
    - GF_SECURITY_ADMIN_USER=admin
    - GF_SECURITY_ADMIN_PASSWORD=admin123
  ports:
    - "3000:3000"
  depends_on:
    - prometheus
```

![1 docker-compose](https://github.com/user-attachments/assets/0a337d3c-ecc0-4c9e-986c-7d6623344b68)



#### Prometheus metrics from FastAPI
- Created the FastAPI app.
- Loaded the trained PyTorch ResNet18 model (38 plant disease classes).
- Endpoints:
  - `/` → welcome message.
  - `/health` → returns `{"status":"ok"}` for health checks.
  - `/predict` → accepts an uploaded plant leaf image, runs inference, returns predicted class + confidence.
- **Mounted `/metrics`** using Prometheus’ official `make_asgi_app()`:
  ```python
  from prometheus_client import make_asgi_app
  metrics_app = make_asgi_app()
  app.mount("/metrics", metrics_app)
  ```
<img width="1362" height="686" alt="image" src="https://github.com/user-attachments/assets/ce5191ef-2c4e-416a-8751-2d3b4e4c551a" />

<img width="1280" height="658" alt="image" src="https://github.com/user-attachments/assets/1aa61a9e-d772-4478-aff7-24a9543ec09f" />


Prometheus scrapes our app at app:8000/metrics every 5s.
app is the service name from Docker Compose, so Prometheus can reach it over the Compose network instead of localhost. This is how you're supposed to wire Prometheus ↔ FastAPI in Docker.

<img width="648" height="558" alt="prometheus ss" src="https://github.com/user-attachments/assets/7c81e900-62cb-455a-893b-84ba6ab190dc" />


#### Grafana Setup
1. Open Grafana (port 3000 from Docker / Codespaces).
2. Log in with the admin credentials from docker-compose.yml.
3. Add Prometheus as a data source:
- Connections → Add new data source → Prometheus
- URL: http://prometheus:9090
- Save & Test
Using the service name prometheus:9090 (not localhost) is the correct way when Grafana and Prometheus run in Docker Compose.
4. Create dashboards:
- Add a panel
- Query our metrics (request latency histogram, tokens_per_call, etc.)

Once the data source is connected, we create panels that query our FastAPI metrics exposed at /metrics:
- Request latency histogram (p95 per endpoint)
- Request rate / throughput (calls/sec)
- tokens_per_call (request cost / size)
This is the normal Prometheus → Grafana workflow: Prometheus scrapes our FastAPI /metrics, then Grafana queries Prometheus and plots those time series.

![grafana connection](https://github.com/user-attachments/assets/1efe91c4-6699-4088-98ae-70dad97a1190)

<img width="1280" height="658" alt="image" src="https://github.com/user-attachments/assets/21cd08ee-a393-4944-9637-8eb342a82de2" />


#### Docker-compose to bring it all together
- app runs the FastAPI model server with Uvicorn on 0.0.0.0:8000 so other containers can reach it (this is required in Docker).
- prometheus scrapes app.
- grafana connects to Prometheus.

-To run the setup,
```bash
docker compose down
docker compose up --build
```
