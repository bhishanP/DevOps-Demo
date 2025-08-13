from app.app import create_app

def test_index():
    app = create_app()
    client = app.test_client()
    r = client.get("/")
    assert r.status_code == 200
    assert r.get_json()["message"].startswith("Hello")

def test_metrics():
    app = create_app()
    client = app.test_client()
    client.get("/")
    client.get("/slow?ms=10")
    m = client.get("/metrics")
    assert m.status_code == 200
    assert b"demo_requests_total" in m.data
