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
