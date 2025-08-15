# DevOps Demo

A compact DevOps demo featuring a Flask web app instrumented with Prometheus metrics, visualized in Grafana, containerized with Docker, and deployable to Kubernetes with a GitHub Actions pipeline.

## Features

- **Flask** API with `/`, `/metrics`, `/healthz`, `/readyz`, and `/slow?ms=…`
- **Prometheus** scraping the app’s `/metrics`
- **Grafana** preprovisioned datasource + dashboard (`Flask App – Overview`)
- **Docker / docker-compose** for local dev
- **Kubernetes** manifests (Deployment, Service, optional Ingress & HPA)
- **GitHub Actions** CI: build → smoke test → push to **GHCR** → deploy app + monitoring (self-hosted runner)


## Architecture

```

\[Flask App] <-- /metrics --> \[Prometheus] ---> \[Grafana]
^                                     (preprovisioned datasource + dashboard)
+----- Docker / Kubernetes (Deployment, Service, optional HPA/Ingress)

````

---

## Quick Start (Local via docker-compose)

1. **Clone**
   ```bash
   git clone https://github.com/bhishanP/DevOps-Demo.git
   cd DevOps-Demo
   ```

2. **Up**

   ```bash
   docker compose up --build
   ```

3. **Open**

   * Flask: [http://localhost:8000/](http://localhost:8000/)
   * Prometheus: [http://localhost:9090/](http://localhost:9090/)
   * Grafana: [http://localhost:3000/](http://localhost:3000/)

---

## Kubernetes

You can deploy either **via CI** (recommended) or **manually**.

### A) Deploy via GitHub Actions (recommended)

* A self-hosted runner with `kubectl` access to your local cluster runs the workflow:

  * Builds image → **smoke tests** it
  * Pushes to **GHCR**: `ghcr.io/bhishanp/flask-prom-grafana-devops:{latest, <commit-sha>}`
  * Applies `k8s/deployment.yaml`, sets image to the commit SHA
  * Creates ConfigMaps from `prometheus/` & `grafana/`, then applies:

    * `k8s/prometheus_deploy.yml`
    * `k8s/grafana_deploy.yml`

Trigger:

* Push to `main`, open a PR to `main`, or run manually (**Actions → CI → Run workflow**).

**View UIs (minikube examples):**

```bash
# Prometheus
kubectl -n monitoring port-forward svc/prometheus 9090:9090
# -> http://localhost:9090 (Status -> Targets should be UP)

# Grafana
kubectl -n monitoring port-forward svc/grafana 3000:80
# -> http://localhost:3000 (Dashboard: "Flask App - Overview")
```

### B) Manual apply (if you prefer CLI)

1. **App**

```bash
kubectl apply -f k8s/deployment.yaml
# (optional)
kubectl apply -f k8s/ingress.yaml || true
kubectl apply -f k8s/hpa.yaml || true
```

2. **Monitoring**

```bash
kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -

# Prometheus config → ConfigMap
kubectl create configmap prometheus-config -n monitoring \
  --from-file=prometheus/prometheus.yml \
  --dry-run=client -o yaml | kubectl apply -f -

# Grafana provisioning (separate CMs for each subdir)
kubectl create configmap grafana-datasources -n monitoring \
  --from-file=grafana/provisioning/datasources \
  --dry-run=client -o yaml | kubectl apply -f -

kubectl create configmap grafana-dashboard-provider -n monitoring \
  --from-file=grafana/provisioning/dashboards \
  --dry-run=client -o yaml | kubectl apply -f -

kubectl create configmap grafana-dashboards -n monitoring \
  --from-file=grafana/dashboards \
  --dry-run=client -o yaml | kubectl apply -f -

# Deployments + Services
kubectl apply -f k8s/prometheus_deploy.yml
kubectl apply -f k8s/grafana_deploy.yml
```

3. **Open**

```bash
kubectl port-forward svc/flask-prom-grafana-devops 8000:80
kubectl -n monitoring port-forward svc/prometheus 9090:9090
kubectl -n monitoring port-forward svc/grafana 3000:80
```

> `prometheus/prometheus.yml` points at your Service DNS:
>
> ```yaml
> scrape_configs:
>   - job_name: 'flask-service'
>     metrics_path: /metrics
>     static_configs:
>       - targets:
>           - 'flask-prom-grafana-devops.default.svc.cluster.local:80'
> ```

---

## Endpoints

| Endpoint      | Description                  |
| ------------- | ---------------------------- |
| `/`           | Hello message + metadata     |
| `/metrics`    | Prometheus metrics           |
| `/healthz`    | Liveness probe               |
| `/readyz`     | Readiness probe              |
| `/slow?ms=10` | Simulate slow request (10ms) |

---

## CI/CD

* Workflow: [.github/workflows/ci.yml](.github/workflows/ci.yml)
* Steps: **Build → Smoke test → Push to GHCR → kubectl apply → set image to `${{ github.sha }}` → deploy Prometheus & Grafana**
* Images:

  * App: `ghcr.io/bhishanp/flask-prom-grafana-devops:{latest, <sha>}`
  * Prometheus: pinned in `k8s/prometheus_deploy.yml` (you can pin a version)
  * Grafana: pinned in `k8s/grafana_deploy.yml` (you can pin a version)

> The workflow expects a **self-hosted runner** that already has a working kubeconfig for your local cluster.

---

## File Structure

```
.github/                      # GitHub Actions workflow
app/                          # Flask app
grafana/
  provisioning/
    datasources/datasource.yml
    dashboards/dashboard.yml
  dashboards/
    flask-overview.json       # prebuilt dashboard
prometheus/
  prometheus.yml              # Prometheus scrape config
k8s/
  deployment.yaml             # App Deployment + Service
  ingress.yaml                # (optional) Ingress
  hpa.yaml                    # (optional) HorizontalPodAutoscaler
  prometheus_deploy.yml       # Prometheus Deployment + Service (ns: monitoring)
  grafana_deploy.yml          # Grafana Deployment + Service (ns: monitoring)
```

---

## Troubleshooting

* **Grafana shows provisioning errors**
  Ensure these CMs exist and are mounted to the right paths:

  * `grafana-datasources` → `/etc/grafana/provisioning/datasources`
  * `grafana-dashboard-provider` → `/etc/grafana/provisioning/dashboards`
  * `grafana-dashboards` → `/var/lib/grafana/dashboards`

  Restart Grafana to pick up changes:

  ```bash
  kubectl -n monitoring rollout restart deploy/grafana
  ```

* **Prometheus target is DOWN**
  Check the target host in `prometheus/prometheus.yml`, reapply the ConfigMap, and restart:

  ```bash
  kubectl -n monitoring create configmap prometheus-config \
    --from-file=prometheus/prometheus.yml \
    -o yaml --dry-run=client | kubectl apply -f -
  kubectl -n monitoring rollout restart deploy/prometheus
  ```

* **HPA doesn’t scale**
  Ensure `metrics-server` is installed (`kubectl top pods` works).

---

## Development

* Update deps in [requirements.txt](requirements.txt)
* (Optional) run tests if present:

  ```bash
  pytest -q
  ```
