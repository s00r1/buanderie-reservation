import os
import sys
import tempfile

import pytest

# Configure a temporary data file before importing the app
DATA_FILE = os.path.join(tempfile.gettempdir(), "test_reservations.json")
os.environ["RESERVATIONS_FILE"] = DATA_FILE
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
