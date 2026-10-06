from fastapi.testclient import TestClient
from backend.app.main import app
import uuid


client = TestClient(app)


def login_admin():
    response = client.post(
        "/auth/login",
        json={
            "username": "admin",
            "password": "Admin123"
        }
    )

    assert response.status_code == 200

    token = response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }


def test_admin_can_create_plant():
    headers = login_admin()

    unique_id = uuid.uuid4().hex[:8]

    response = client.post(
        "/plants",
        headers=headers,
        json={
            "name": f"Test Santral {unique_id}",
            "type": "TEST",
            "province": "Konya",
            "installed_power_mw": 100.50,
            "commissioning_year": 2026,
            "plant_code": f"TEST-PLANT-{unique_id}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Plant created"
    assert data["plant"]["name"] == f"Test Santral {unique_id}"
    assert data["plant"]["plant_code"] == f"TEST-PLANT-{unique_id}"

    plant_id = data["plant"]["id"]

    # Test verisini temizle
    delete_response = client.delete(
        f"/plants/{plant_id}",
        headers=headers
    )

    assert delete_response.status_code == 200


def test_duplicate_plant_code_rejected():
    headers = login_admin()

    unique_id = uuid.uuid4().hex[:8]
    plant_code = f"TEST-DUPLICATE-{unique_id}"

    first_response = client.post(
        "/plants",
        headers=headers,
        json={
            "name": f"Test Santral 1 {unique_id}",
            "type": "TEST",
            "province": "Konya",
            "installed_power_mw": 50,
            "commissioning_year": 2026,
            "plant_code": plant_code
        }
    )

    assert first_response.status_code == 200

    plant_id = first_response.json()["plant"]["id"]

    second_response = client.post(
        "/plants",
        headers=headers,
        json={
            "name": f"Test Santral 2 {unique_id}",
            "type": "TEST",
            "province": "Adana",
            "installed_power_mw": 75,
            "commissioning_year": 2026,
            "plant_code": plant_code
        }
    )

    assert second_response.status_code == 409

    # Test verisini temizle
    delete_response = client.delete(
        f"/plants/{plant_id}",
        headers=headers
    )

    assert delete_response.status_code == 200


def test_admin_can_update_plant():
    headers = login_admin()

    unique_id = uuid.uuid4().hex[:8]

    create_response = client.post(
        "/plants",
        headers=headers,
        json={
            "name": f"Eski Santral {unique_id}",
            "type": "TEST",
            "province": "Konya",
            "installed_power_mw": 100,
            "commissioning_year": 2025,
            "plant_code": f"TEST-UPDATE-{unique_id}"
        }
    )

    assert create_response.status_code == 200

    plant_id = create_response.json()["plant"]["id"]

    update_response = client.put(
        f"/plants/{plant_id}",
        headers=headers,
        json={
            "name": f"Güncellenmiş Santral {unique_id}",
            "type": "GÜNCEL",
            "province": "Adana",
            "installed_power_mw": 250.75,
            "commissioning_year": 2026,
            "plant_code": f"TEST-UPDATE-{unique_id}"
        }
    )

    assert update_response.status_code == 200

    data = update_response.json()

    assert data["message"] == "Plant updated"
    assert data["plant"]["name"] == f"Güncellenmiş Santral {unique_id}"
    assert data["plant"]["province"] == "Adana"
    assert data["plant"]["installed_power_mw"] == 250.75

    # Test verisini temizle
    delete_response = client.delete(
        f"/plants/{plant_id}",
        headers=headers
    )

    assert delete_response.status_code == 200


def test_plant_creation_requires_authentication():
    unique_id = uuid.uuid4().hex[:8]

    response = client.post(
        "/plants",
        json={
            "name": f"Unauthorized Plant {unique_id}",
            "type": "TEST",
            "province": "Konya",
            "installed_power_mw": 100,
            "commissioning_year": 2026,
            "plant_code": f"UNAUTHORIZED-{unique_id}"
        }
    )

    assert response.status_code == 401


def test_admin_can_delete_non_existing_plant():
    headers = login_admin()

    response = client.delete(
        "/plants/999999",
        headers=headers
    )

    assert response.status_code == 200

    assert response.json() == {
        "message": "Plant not found"
    }