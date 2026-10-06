from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def login_admin():
    response = client.post(
        "/auth/login",
        json={
            "username": "admin",
            "password": "Admin123"
        },
    )

    assert response.status_code == 200

    token = response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }


def test_admin_can_create_equipment():
    headers = login_admin()

    response = client.post(
        "/equipment",
        headers=headers,
        json={
            "equipment_code": "TEST-EQP-001",
            "name": "Test Ekipmanı",
            "type": "TEST",
            "criticality": "DUSUK",
            "plant_id": 1,
            "plant_code": "TEST-PLANT"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Equipment created"
    assert data["equipment"]["equipment_code"] == "TEST-EQP-001"

    equipment_id = data["equipment"]["id"]

    delete_response = client.delete(
        f"/equipment/{equipment_id}",
        headers=headers
    )

    assert delete_response.status_code == 200


def test_duplicate_equipment_code_rejected():
    headers = login_admin()

    first_response = client.post(
        "/equipment",
        headers=headers,
        json={
            "equipment_code": "TEST-EQP-002",
            "name": "Test Ekipmanı 2",
            "type": "TEST",
            "criticality": "ORTA",
            "plant_id": 1,
            "plant_code": "TEST-PLANT"
        }
    )

    assert first_response.status_code == 200

    equipment_id = first_response.json()["equipment"]["id"]

    second_response = client.post(
        "/equipment",
        headers=headers,
        json={
            "equipment_code": "TEST-EQP-002",
            "name": "Duplicate Ekipman",
            "type": "TEST",
            "criticality": "YUKSEK",
            "plant_id": 1,
            "plant_code": "TEST-PLANT"
        }
    )

    assert second_response.status_code == 409

    delete_response = client.delete(
        f"/equipment/{equipment_id}",
        headers=headers
    )

    assert delete_response.status_code == 200


def test_admin_can_update_equipment():
    headers = login_admin()

    create_response = client.post(
        "/equipment",
        headers=headers,
        json={
            "equipment_code": "TEST-EQP-003",
            "name": "Eski Ekipman",
            "type": "TEST",
            "criticality": "ORTA",
            "plant_id": 1,
            "plant_code": "TEST-PLANT"
        }
    )

    assert create_response.status_code == 200

    equipment_id = create_response.json()["equipment"]["id"]

    update_response = client.put(
        f"/equipment/{equipment_id}",
        headers=headers,
        json={
            "equipment_code": "TEST-EQP-003",
            "name": "Güncellenmiş Ekipman",
            "type": "GÜNCEL",
            "criticality": "YUKSEK",
            "plant_id": 1,
            "plant_code": "TEST-PLANT"
        }
    )

    assert update_response.status_code == 200

    data = update_response.json()

    assert data["message"] == "Equipment updated"
    assert data["equipment"]["name"] == "Güncellenmiş Ekipman"
    assert data["equipment"]["criticality"] == "YUKSEK"

    delete_response = client.delete(
        f"/equipment/{equipment_id}",
        headers=headers
    )

    assert delete_response.status_code == 200


def test_equipment_requires_authentication():
    response = client.post(
        "/equipment",
        json={
            "equipment_code": "UNAUTHORIZED-001",
            "name": "Unauthorized Equipment",
            "type": "TEST",
            "criticality": "DUSUK",
            "plant_id": 1,
            "plant_code": "TEST"
        }
    )

    assert response.status_code == 401


def test_admin_can_delete_non_existing_equipment():
    headers = login_admin()

    response = client.delete(
        "/equipment/999999",
        headers=headers
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Equipment not found"
    }