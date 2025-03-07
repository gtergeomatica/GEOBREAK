import requests
import pytest
from datetime import datetime
import os

# Modifica questa variabile in base all'URL in cui l'API è in esecuzione
BASE_URL = os.getenv("BASE_BACKEND_URL","http://localhost:8000")

def test_create_sensor():
    sensor_data = {
        "name": "Sensore Test",
        "value": 23.5,
        "timestamp": "2025-03-07T12:00:00"
    }
    response = requests.post(f"{BASE_URL}/sensors", json=sensor_data)
    assert response.status_code == 201
    data = response.json()
    # Verifica che l'ID sia stato assegnato e che i campi siano corretti
    assert "id" in data
    assert data["name"] == sensor_data["name"]
    assert data["value"] == sensor_data["value"]
    # Il formato della data potrebbe variare, verifichiamo che contenga la data inviata
    assert sensor_data["timestamp"] in data["timestamp"]

def test_read_sensors():
    # Creiamo un sensore in modo da avere almeno un elemento nell'elenco
    sensor_data = {
        "name": "Sensore Lista",
        "value": 55.0,
        "timestamp": "2025-03-07T13:00:00"
    }
    create_resp = requests.post(f"{BASE_URL}/sensors", json=sensor_data)
    assert create_resp.status_code == 201
    created_sensor = create_resp.json()
    
    response = requests.get(f"{BASE_URL}/sensors")
    assert response.status_code == 200
    sensors = response.json()
    # Verifica che la lista contenga il sensore appena creato
    assert any(s["id"] == created_sensor["id"] for s in sensors)

def test_get_sensor():
    # Creazione di un sensore per il test
    sensor_data = {
        "name": "Sensore Singolo",
        "value": 10.0,
        "timestamp": "2025-03-07T14:00:00"
    }
    create_resp = requests.post(f"{BASE_URL}/sensors", json=sensor_data)
    assert create_resp.status_code == 201
    sensor_id = create_resp.json()["id"]

    # Recupero del sensore esistente
    response = requests.get(f"{BASE_URL}/sensors/{sensor_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == sensor_id
    assert data["name"] == sensor_data["name"]

    # Verifica per un sensore inesistente
    response = requests.get(f"{BASE_URL}/sensors/99999")
    assert response.status_code == 404

def test_update_sensor():
    # Creazione del sensore iniziale
    sensor_data = {
        "name": "Sensore Update",
        "value": 100.0,
        "timestamp": "2025-03-07T15:00:00"
    }
    create_resp = requests.post(f"{BASE_URL}/sensors", json=sensor_data)
    assert create_resp.status_code == 201
    sensor_id = create_resp.json()["id"]

    # Dati per l'aggiornamento completo (PUT)
    new_sensor_data = {
        "id": sensor_id,  # Se il modello prevede questo campo
        "name": "Sensore Aggiornato",
        "value": 150.0,
        "timestamp": "2025-03-07T16:00:00"
    }
    response = requests.put(f"{BASE_URL}/sensors/{sensor_id}", json=new_sensor_data)
    assert response.status_code == 200
    updated_sensor = response.json()
    assert updated_sensor["name"] == "Sensore Aggiornato"
    assert updated_sensor["value"] == 150.0

    # Aggiornamento di un sensore inesistente
    response = requests.put(f"{BASE_URL}/sensors/99999", json=new_sensor_data)
    assert response.status_code == 404

def test_patch_sensor():
    # Creazione del sensore iniziale
    sensor_data = {
        "name": "Sensore Patch",
        "value": 200.0,
        "timestamp": "2025-03-07T17:00:00"
    }
    create_resp = requests.post(f"{BASE_URL}/sensors", json=sensor_data)
    assert create_resp.status_code == 201
    sensor_id = create_resp.json()["id"]

    # Dati per aggiornamento parziale (PATCH)
    patch_data = {
        "value": 250.0
    }
    response = requests.patch(f"{BASE_URL}/sensors/{sensor_id}", json=patch_data)
    assert response.status_code == 200
    patched_sensor = response.json()
    assert patched_sensor["value"] == 250.0
    # Gli altri campi non devono essere modificati
    assert patched_sensor["name"] == sensor_data["name"]

    # PATCH su un sensore inesistente
    response = requests.patch(f"{BASE_URL}/sensors/99999", json=patch_data)
    assert response.status_code == 404

def test_delete_sensor():
    # Creazione del sensore da eliminare
    sensor_data = {
        "name": "Sensore Delete",
        "value": 300.0,
        "timestamp": "2025-03-07T18:00:00"
    }
    create_resp = requests.post(f"{BASE_URL}/sensors", json=sensor_data)
    assert create_resp.status_code == 201
    sensor_id = create_resp.json()["id"]

    # Eliminazione del sensore
    response = requests.delete(f"{BASE_URL}/sensors/{sensor_id}")
    assert response.status_code == 204

    # Verifica che il sensore sia stato eliminato
    response = requests.get(f"{BASE_URL}/sensors/{sensor_id}")
    assert response.status_code == 404

    # Eliminazione di un sensore inesistente
    response = requests.delete(f"{BASE_URL}/sensors/99999")
    assert response.status_code == 404
