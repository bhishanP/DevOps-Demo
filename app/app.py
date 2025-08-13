from flask import Flask, jsonify, request
import time
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import Counter, Histogram

metrics_info = {
    "app_name": "flask-prom-grafana-devops",
    "version": "0.1.0",
    "env": "dev"
}

REQUEST_COUNT = Counter('demo_requests_total', 'Total number of demo requests', ['endpoint'])
REQUEST_LATENCY = Histogram('demo_request_duration_seconds', 'Request latency', ['endpoint'])

def create_app():
    app = Flask(__name__)
    PrometheusMetrics(app, path="/metrics")

    @app.route("/")
    def index():
        REQUEST_COUNT.labels(endpoint="/").inc()
        return jsonify({"message": "Hello from Flask with Prometheus & Grafana!", **metrics_info})

    @app.route("/healthz")
    def health():
        return jsonify({"status": "ok"}), 200

    @app.route("/readyz")
    def ready():
        return jsonify({"status": "ready"}), 200

    @app.route("/slow")
    def slow():
        ms = int(request.args.get("ms", "300"))
        start = time.time()
        time.sleep(ms / 1000.0)
        REQUEST_LATENCY.labels(endpoint="/slow").observe(time.time() - start)
        REQUEST_COUNT.labels(endpoint="/slow").inc()
        return jsonify({"slept_ms": ms})

    return app

app = create_app()
