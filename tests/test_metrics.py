from src.utils.metrics import HTTP_LATENCY, HTTP_REQUESTS


def test_metrics_labels():
    HTTP_REQUESTS.labels(method="GET", path="/x", status="200").inc()
    HTTP_LATENCY.labels(method="GET", path="/x").observe(0.1)
