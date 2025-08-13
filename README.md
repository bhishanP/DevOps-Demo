# DevOps Demo

A modern DevOps demo project featuring a Flask web application instrumented with Prometheus metrics, visualized in Grafana, and ready for deployment with Docker and Kubernetes.

## Features

- **Flask** web API with health, readiness, and demo endpoints
- **Prometheus** metrics via [`prometheus_flask_exporter`](https://github.com/rycus86/prometheus_flask_exporter)
- **Grafana** dashboards for real-time monitoring
- **Docker** and **docker-compose** for local development
- **Kubernetes** manifests for production deployment, including HPA, Ingress, and ServiceMonitor
- **GitHub Actions** CI for testing, building, and deploying

## Architecture

```
[Flask App] <--/metrics--> [Prometheus] <---> [Grafana]
     |                                   ^
     |                                   |
     +---[Docker/K8s]--------------------+
```

## Quick Start (Local)

1. **Clone the repo**
   ```sh
   git clone https://github.com/bhishanP/DevOps-Demo.git
   cd DevOps-Demo
   ```

2. **Start all services**
   ```sh
   docker-compose up --build
   ```

3. **Access the services:**
   - Flask API: [http://localhost:8000/](http://localhost:8000/)
   - Prometheus: [http://localhost:9090/](http://localhost:9090/)
   - Grafana: [http://localhost:3000/](http://localhost:3000/)

## Endpoints

| Endpoint      | Description                |
|---------------|---------------------------|
| `/`           | Hello message + metadata   |
| `/metrics`    | Prometheus metrics         |
| `/healthz`    | Health check (for K8s)    |
| `/readyz`     | Readiness check (for K8s) |
| `/slow?ms=10` | Simulate slow request     |

## Monitoring

- **Prometheus** scrapes metrics from `/metrics` endpoint.
- **Grafana** dashboard: see [grafana/dashboards/flask-overview.json](grafana/dashboards/flask-overview.json).

## Kubernetes

- Deploy with:
  ```sh
  kubectl apply -f k8s/deployment.yaml
  kubectl apply -f k8s/ingress.yaml
  kubectl apply -f k8s/hpa.yaml
  ```

## CI/CD

- Automated tests and Docker builds via [GitHub Actions](.github/workflows/ci.yml).

## Development

- Run tests:
  ```sh
  pytest -q
  ```
- Add dependencies to [requirements.txt](requirements.txt).

## File Structure

```
.github/       # GitHub Actions workflows
app/           # Flask app source code
tests/         # Pytest unit tests
grafana/       # Dashboards & provisioning
prometheus/    # Prometheus config
k8s/           # Kubernetes manifests

```