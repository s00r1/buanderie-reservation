import os
import sys
import tempfile

import pytest

# Configure a temporary data file before importing the app
DATA_FILE = os.path.join(tempfile.gettempdir(), "test_reservations.json")
os.environ["RESERVATIONS_FILE"] = DATA_FILE
os.environ["ADMIN_CODE"] = "s00r1"
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app import app, DATA_FILE as APP_DATA_FILE, load_reservations

@pytest.fixture(autouse=True)
def cleanup():
    if os.path.exists(APP_DATA_FILE):
        os.remove(APP_DATA_FILE)
    yield
    if os.path.exists(APP_DATA_FILE):
        os.remove(APP_DATA_FILE)

@pytest.fixture
def client():
    return app.test_client()

def test_successful_reservation(client):
    payload = {
        "code": "1234",
        "date": "2025-01-01",
        "heure": "08:00",
        "tournees": 1,
        "machine": "lave-linge",
        "chambre": "1",
    }
    response = client.post("/reserver", json=payload)
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"
    reservations = load_reservations()
    assert len(reservations) == 1
    assert reservations[0]["start"] == "2025-01-01T08:00"


def test_invalid_code_rejected(client):
    payload = {
        "code": "abcd",  # invalid
        "date": "2025-01-01",
        "heure": "09:00",
        "tournees": 1,
        "machine": "lave-linge",
        "chambre": "1",
    }
    response = client.post("/reserver", json=payload)
    assert response.status_code == 400
    assert "Format de code" in response.get_json()["message"]
    assert load_reservations() == []


def test_duplicate_reservation_conflict(client):
    payload = {
        "code": "1234",
        "date": "2025-01-01",
        "heure": "10:00",
        "tournees": 1,
        "machine": "lave-linge",
        "chambre": "1",
    }
    first = client.post("/reserver", json=payload)
    assert first.status_code == 200
    second = client.post("/reserver", json=payload)
    assert second.status_code == 409
    assert "déjà réservé" in second.get_json()["message"]
    reservations = load_reservations()
    assert len(reservations) == 1


def test_admin_can_delete_any_reservation(client):
    payload = {
        "code": "1111",
        "date": "2025-01-02",
        "heure": "08:00",
        "tournees": 1,
        "machine": "lave-linge",
        "chambre": "2",
    }
    # create reservation with regular code
    resp = client.post("/reserver", json=payload)
    assert resp.status_code == 200

    # admin deletes it using the admin code
    delete_payload = {"start": "2025-01-02T08:00", "code": "s00r1"}
    delete = client.post("/delete_reservation", json=delete_payload)
    assert delete.status_code == 200
    assert delete.get_json()["status"] == "deleted"
    assert load_reservations() == []


def test_overlapping_reservation_rejected(client):
    first = {
        "code": "1234",
        "date": "2025-01-03",
        "heure": "12:00",
        "tournees": 2,
        "machine": "lave-linge",
        "chambre": "1",
    }
    second = {
        "code": "5678",
        "date": "2025-01-03",
        "heure": "13:00",
        "tournees": 1,
        "machine": "lave-linge",
        "chambre": "2",
    }

    resp1 = client.post("/reserver", json=first)
    assert resp1.status_code == 200
    resp2 = client.post("/reserver", json=second)
    assert resp2.status_code == 409
    assert "déjà réservé" in resp2.get_json()["message"]
    reservations = load_reservations()
    assert len(reservations) == 1


def test_get_reservations_hides_code(client):
    payload = {
        "code": "1234",
        "date": "2025-01-04",
        "heure": "15:00",
        "tournees": 1,
        "machine": "lave-linge",
        "chambre": "3",
    }
    resp = client.post("/reserver", json=payload)
    assert resp.status_code == 200

    resp = client.get("/get_reservations")
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert data
    assert "code" not in data[0]
