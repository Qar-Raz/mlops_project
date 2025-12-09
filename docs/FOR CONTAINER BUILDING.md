# Monitoring & Observability Setup

This document outlines the monitoring infrastructure implemented for the MLOps project, utilizing **Prometheus** for metric collection and **Grafana** for visualization.

## 1. Architecture Overview

The system consists of three Docker containers orchestrated via Docker Compose:

1.  **FastAPI Backend (`app`)**: Serves the LLM/CV models and exposes metrics.
2.  **Prometheus**: Scrapes metrics from the backend every 5 seconds.
3.  **Grafana**: Visualizes the metrics in a pre-configured dashboard.

## 2. Quick Start

**Directory:** Run these commands from the root of the repository (`mlops_project/`).

### Build and Run
To build the optimized images and start the entire stack:

```bash
docker-compose up -d --build
```

### Stop Services
To stop all containers and free up ports:

```bash
docker-compose down
```

## 3. Service Endpoints & Port Mappings

| Service | Internal Port | Host Port | URL | Description |
| :--- | :--- | :--- | :--- | :--- |
| **Backend** | 8000 | **8000** | [http://localhost:8000/metrics](http://localhost:8000/metrics) | Raw metrics endpoint (Prometheus format). |
| **Prometheus** | 9090 | **9090** | [http://localhost:9090](http://localhost:9090) | Prometheus UI (for debugging queries). |
| **Grafana** | 3000 | **3000** | [http://localhost:3000](http://localhost:3000) | Main Dashboard UI. |

## 4. Configuration Details

### Prometheus (`prometheus.yml`)
Located in the root directory. It defines the scrape targets.
```yaml
scrape_configs:
  - job_name: 'fastapi_app'
    static_configs:
      - targets: ['app:8000'] # Connects to the backend container internally
```

### Grafana Configuration (`grafana/`)
The Grafana setup is fully **provisioned**, meaning no manual setup is required in the UI.

#### Folder Structure
```text
grafana/
├── dashboards/
│   └── main_dashboard.json       # The actual JSON definition of the UI panels
├── provisioning/
│   ├── dashboards/
│   │   └── dashboard.yml         # Tells Grafana where to find json files
│   └── datasources/
│       └── datasource.yml        # Configures the connection to Prometheus
```

*   **`datasource.yml`**: Automatically adds Prometheus as a data source.
*   **`dashboard.yml`**: Automatically loads `main_dashboard.json` from the disk.

## 5. Metrics Implemented

We switched from `psutil` (which had issues inside Docker) to standard Python libraries for system health:

*   **LLM Token Usage**: `llm_token_usage_total` (Counter)
*   **Latency**: `app_request_latency_seconds` (Histogram)
*   **Concurrency**: `system_active_threads` (Gauge using `threading.active_count()`)
*   **Storage Health**: `system_disk_usage_percent` (Gauge using `shutil.disk_usage()`)
*   **Guardrails**: `guard_failures_total` (Counter)

## 6. Troubleshooting & Administration

### Reset Grafana Admin Password
If you cannot log in to Grafana (default user: `admin`), run this command while the container is running:

```bash
docker exec -it grafana grafana-cli admin reset-admin-password admin
```
*This resets the password to `admin`.*

### "Metrics returning 0.0"
If system metrics appear as 0:
1.  Ensure you are looking at the **Active Threads** or **Disk Usage** panels, not the old CPU/RAM panels.
2.  Check the backend logs: `docker-compose logs -f app`

## 7. Data Persistence (Volumes)

We use Docker **Volumes** to ensure data isn't lost when containers restart.

*   **`prometheus_data`**: Stores the history of your metrics (time-series data). If you delete this volume, your historical graphs will be reset.
*   **`grafana_data`**: Stores your Grafana user accounts (admin password), sessions, and any dashboards you create manually in the UI.
*   **`./backend:/backend` (Bind Mount)**: This maps your local code folder into the container. This is used for **development** so that changes to `app.py` are reflected immediately (via `uvicorn --reload`) without rebuilding the image.

> **Important for Cloud Deployment:**
> *   **Code (`app.py`)**: This is **NOT** sent to the cloud via the volume. It is baked into the image itself because of the `COPY . .` line in the `Dockerfile`.
> *   **Data (`prometheus_data`)**: This data is **NOT** sent to the cloud. When you deploy to ACR/Azure, your volumes start empty. You will not see your local metric history in the cloud.
> *   **Bind Mounts**: The `./backend:/backend` mapping is ignored or invalid in most cloud container environments. The cloud container relies entirely on the code inside the image.

## 8. Cloud Deployment Guide (Azure/ACR)

### Do I need to change the config?
**No.** The internal communication between containers (`prometheus` -> `app:8000`) happens inside the Docker network. Even in the cloud, as long as they are running in the same task/pod/compose group, they will find each other using the service name `app`.

### How does Prometheus find the backend?
Prometheus uses the internal Docker DNS name `app`. It does **not** use the public IP or public URL. It stays entirely inside the private network.

### How do I connect my Frontend?
Yes, you simply update your frontend configuration to point to the **Public URL** of your deployed backend.
*   **Local**: `http://localhost:8000`
*   **Cloud**: `https://your-app-service-name.azurewebsites.net`

### Deployment Considerations (Single IP)
If you deploy to a service that exposes a single IP (like Azure App Service for Containers):
1.  **Ports**: You will likely need to configure the App Service to expose the ports, or use a **Reverse Proxy** (like Nginx) container to route traffic:
    *   `domain.com/api` -> `app:8000`
    *   `domain.com/grafana` -> `grafana:3000`
2.  **Firewall**: If deploying to a VM, ensure your Network Security Group (NSG) allows inbound traffic on ports `8000` (API) and `3000` (Grafana).

## 8. Cloud Deployment Guide (Azure/ACR)

### Do I need to change the config?
**No.** The internal communication between containers (`prometheus` -> `app:8000`) happens inside the Docker network. Even in the cloud, as long as they are running in the same task/pod/compose group, they will find each other using the service name `app`.

### How does Prometheus find the backend?
Prometheus uses the internal Docker DNS name `app`. It does **not** use the public IP or public URL. It stays entirely inside the private network.

### How do I connect my Frontend?
Yes, you simply update your frontend configuration to point to the **Public URL** of your deployed backend.
*   **Local**: `http://localhost:8000`
*   **Cloud**: `https://your-app-service-name.azurewebsites.net`

### Deployment Considerations (Single IP)
If you deploy to a service that exposes a single IP (like Azure App Service for Containers):
1.  **Ports**: You will likely need to configure the App Service to expose the ports, or use a **Reverse Proxy** (like Nginx) container to route traffic:
    *   `domain.com/api` -> `app:8000`
    *   `domain.com/grafana` -> `grafana:3000`
2.  **Firewall**: If deploying to a VM, ensure your Network Security Group (NSG) allows inbound traffic on ports `8000` (API) and `3000` (Grafana).
