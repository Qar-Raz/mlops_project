# MLOPS_PROJECT — Plant Disease Detection (with Monitoring)

**Last updated:** December, 2025


This version highlights that the backend image is built and pushed to **Azure ACR** via GitHub Actions and the service is deployed to **Azure Container Instances / Container Apps**. It also documents the local **Prometheus → Grafana** monitoring setup that scrapes the Azure-deployed backend.

---

# Table of contents

* [Project Summary](#project-summary)
* [What this delivers](#what-this-delivers)
* [Architecture Overview](#architecture-overview)
* [Repository Layout](#repository-layout)
* [Prerequisites](#prerequisites)
* [CI / CD (Build & Push to ACR)](#ci--cd-build--push-to-acr)
* [Deploy to Azure Container Instance (ACI)](#deploy-to-azure-container-instance-aci)
* [Local Monitoring: Prometheus + Grafana](#local-monitoring-prometheus--grafana)
* [Grafana Provisioning & Dashboard](#grafana-provisioning--dashboard)
* [Verification Checklist](#verification-checklist)
* [Troubleshooting](#troubleshooting)
* [Security & Best Practices](#security--best-practices)
* [Useful Commands (cheat sheet)](#useful-commands-cheat-sheet)
* [Future Improvements](#future-improvements)
* [Contact / Next Steps](#contact--next-steps)

---

## Project summary

This repo contains a FastAPI service that serves a PyTorch model for plant disease detection (38 classes). The CI/CD workflow builds the Docker image and pushes it to **Azure Container Registry (ACR)**. The app is deployed to Azure (ACI / Container Apps) and exposes Prometheus metrics at `/metrics`. Locally you run Prometheus + Grafana to visualize those metrics.

---

## What this delivers

* FastAPI inference service (PyTorch ResNet18)
* Prometheus metrics (latency, request counts, histograms) exposed at `/metrics`
* Grafana dashboards (pre-provisioned) to visualize request rate, avg response size, LLM latency (P50/P95), and alerts
* GitHub Actions workflow: build the image and push to `florabotacr.azurecr.io/flora-backend:latest`
* Docker Compose to run Prometheus + Grafana locally and point Prometheus to the Azure-deployed backend

---

## Architecture overview

```
GitHub Actions (build → push to ACR)
           ↓
Azure Container Registry (ACR)
           ↓
Azure Container Instance / Container Apps (public IP / FQDN)
           ↓
Prometheus (local Docker) scrapes ACI:8000/metrics
           ↓
Grafana (local Docker) queries Prometheus and displays dashboards
```

---

## Repository layout (important files)

```
.
├─ .github/workflows/build-and-push.yml    # builds image and pushes to ACR
├─ docker-compose.yml                      # spins up Prometheus + Grafana locally
├─ prometheus.yml                          # Prometheus config (targets ACI)
└─ grafana/
   ├─ provisioning/
   │  ├─ datasources/datasource.yml       # creates Prometheus datasource (uid: prometheus)
   │  └─ dashboards/provider.yml           # loads dashboards from folder
   └─ dashboards/
      └─ flora-dashboard.json              # pre-built dashboard JSON
```

---

## Prerequisites

* Docker & Docker Compose (to run Prometheus+Grafana locally)
* Azure CLI (`az`) and appropriate Azure permissions
* GitHub repo configured with Actions and secrets for ACR (`ACR_USERNAME`, `ACR_PASSWORD`)
* (Optional) Azure Blob Storage or AWS S3 for model storage

---

## CI / CD — Build & Push to ACR

Your GitHub Actions workflow (`.github/workflows/build-and-push.yml`) does the following:

1. Checks out code, sets up Python
2. Downloads model artifacts (if required)
3. Logs in to ACR using secrets
4. Builds the Docker image and pushes:

   * `florabotacr.azurecr.io/flora-backend:latest`
   * `florabotacr.azurecr.io/flora-backend:${{ github.sha }}`

> Keep ACR credentials in GitHub Secrets or configure a service principal.

---

## Deploy to Azure Container Instance (ACI)

**Example** (replace variables with yours):

```bash
# Login and set subscription
az login
az account set --subscription "<your-subscription-id>"

# Variables
RESOURCE_GROUP="myResourceGroup"
ACI_NAME="flora-aci"
ACR_REGISTRY="florabotacr.azurecr.io"
IMAGE="$ACR_REGISTRY/flora-backend:latest"

# Create resource group (if needed)
az group create -n $RESOURCE_GROUP -l westeurope

# Deploy to ACI (public IP, port 8000)
az container create \
  --resource-group $RESOURCE_GROUP \
  --name $ACI_NAME \
  --image $IMAGE \
  --ports 8000 \
  --ip-address public \
  --registry-login-server $ACR_REGISTRY \
  --registry-username $ACR_USERNAME \
  --registry-password $ACR_PASSWORD \
  --cpu 1 --memory 1.5 \
  --dns-name-label florabackend-demo
```

Get IP / FQDN:

```bash
az container show -g $RESOURCE_GROUP -n $ACI_NAME --query "ipAddress.ip" -o tsv
az container show -g $RESOURCE_GROUP -n $ACI_NAME --query "ipAddress.fqdn" -o tsv
```

Verify endpoints:

```bash
curl -v http://<ACI_IP_or_FQDN>:8000/health
curl -v http://<ACI_IP_or_FQDN>:8000/metrics | head -n 20
```

---

## Local monitoring: Prometheus + Grafana

### `prometheus.yml` example (replace with your ACI IP/FQDN)

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'flora_aci'
    metrics_path: /metrics
    static_configs:
      - targets: ['<ACI_IP_OR_FQDN>:8000']  # e.g. 20.239.244.246:8000
```

### Minimal `docker-compose.yml` (Prometheus + Grafana)

```yaml
version: '3.8'
services:
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    ports:
      - "3000:3000"
    volumes:
      - ./grafana/provisioning:/etc/grafana/provisioning:ro
      - ./grafana/dashboards:/etc/grafana/dashboards:ro
      - grafana_data:/var/lib/grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    depends_on:
      - prometheus
    restart: unless-stopped

volumes:
  prometheus_data:
  grafana_data:
```

Start locally:

```bash
docker-compose up -d
```

* Prometheus UI: `http://localhost:9090/targets`
* Grafana UI: `http://localhost:3000` (default admin/admin or your configured password)

---

## Grafana provisioning & dashboard

### Datasource (auto-provision)

`./grafana/provisioning/datasources/datasource.yml`:

```yaml
apiVersion: 1
datasources:
  - name: Prometheus
    uid: prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: false
```

### Dashboards provider

`./grafana/provisioning/dashboards/provider.yml`:

```yaml
apiVersion: 1
providers:
  - name: 'flora-dashboards'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    options:
      path: /etc/grafana/dashboards
```

### Pre-built dashboard

Place `flora-dashboard.json` in `./grafana/dashboards/`. This dashboard expects the datasource UID `prometheus` and contains panels for:

* Request Rate (requests/sec)
* Avg Response Size (bytes)
* LLM Inference Latency (P50 / P95)
* Active Alerts (ALERTS)

If Grafana shows **“No data source”**:

1. Restart Grafana: `docker-compose restart grafana`
2. Check Grafana logs: `docker logs --tail 200 grafana`
3. Ensure provisioning files are valid YAML and mounted correctly.

---

## Verification checklist (end-to-end)

1. **Metrics endpoint reachable**

```bash
curl -s http://<ACI_IP_or_FQDN>:8000/metrics | head -n 20
```

You should see `# HELP`, `# TYPE`, and metrics names.

2. **Prometheus target is UP**

* Open `http://localhost:9090/targets` → `flora_aci` should be `UP`.

3. **Prometheus query test**

* Open `http://localhost:9090/graph` and run:

  * `rate(http_response_size_bytes_count[1m])`
  * `histogram_quantile(0.95, sum(rate(llm_inference_latency_seconds_bucket[5m])) by (le))`
  * `sum(ALERTS)`

4. **Grafana dashboard**

* Open `http://localhost:3000/d/flora-backend-overview` → panels should show data.

---

## Troubleshooting

### Prometheus target DOWN

* Ensure ACI was created with `--ports 8000` and `--ip-address public` OR the Container App exposes port 8000.
* App must bind to `0.0.0.0` inside the container.
* If ACI in a private VNet, local Prometheus cannot reach it.

### Grafana not starting or provisioning errors

* `docker logs grafana` — look for YAML parse errors or DB permission errors.
* If persistent volume corrupt: remove it (note: this will delete saved dashboards):

  ```bash
  docker-compose down
  docker volume rm grafana_data
  docker-compose up -d
  ```
* Temporarily move provisioning folder to test clean start:

  ```bash
  mv ./grafana/provisioning ./grafana/provisioning.bak
  docker-compose restart grafana
  ```

### Panels empty but Prometheus has data

* Run the dashboard queries in Prometheus UI; if they return series, check datasource UID is `prometheus`.

---

## Security & best practices

* **Do not expose `/metrics` publicly** for production services. Use private monitoring or secure the endpoint (auth / firewall).
* Use Azure Managed Identity or service principals for ACR/S3/Blob access instead of embedded credentials.
* Place production monitoring inside the same VNet/AKS cluster or use a secure remote_write pipeline.
* Use Alertmanager + notification channels for alerts.

---

## Useful commands (cheat sheet)

```bash
# Start monitoring stack
docker-compose up -d

# Prometheus targets page
http://localhost:9090/targets

# Grafana UI
http://localhost:3000

# Restart Grafana
docker-compose restart grafana

# Get ACI IP
az container show -g <rg> -n <name> --query "ipAddress.ip" -o tsv

# Check metrics endpoint
curl -s http://<ACI_IP>:8000/metrics | head -n 20
```

