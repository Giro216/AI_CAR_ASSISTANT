from pathlib import Path
import sys

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import main


client = TestClient(main.app)


def test_list_cars():
    r = client.get("/api/v1/cars")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert {"id", "brand", "model"}.issubset(data[0].keys())


def test_car_detail_ok():
    r = client.get("/api/v1/cars/1")
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == "1"
    assert {"id", "brand", "model"}.issubset(data.keys())


def test_car_detail_404():
    r = client.get("/api/v1/cars/does-not-exist")
    assert r.status_code == 404


def test_filters_meta():
    r = client.get("/api/v1/cars/filters/meta")
    assert r.status_code == 200
    data = r.json()
    assert {"bodyTypes", "fuels", "transmissions", "brands"}.issubset(data.keys())


def test_search():
    r = client.get("/api/v1/cars/search", params={"q": "toy"})
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_pricing_stub():
    r = client.get("/api/v1/cars/1/pricing")
    assert r.status_code == 200
    data = r.json()
    assert data["carId"] == "1"
    assert "history" in data

