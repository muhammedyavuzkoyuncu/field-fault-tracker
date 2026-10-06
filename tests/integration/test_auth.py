from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def login(username, password):
    return client.post(
        "/auth/login",
        json={
            "username": username,
            "password": password,
        },
    )


def test_login_success():
    response = login("admin", "Admin123")

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["username"] == "admin"


def test_login_wrong_password():
    response = login("admin", "WrongPassword123")

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid username or password."


def test_fault_without_token():
    response = client.get("/faults")

    assert response.status_code == 401


def test_create_fault_without_token():
    response = client.post(
        "/faults",
        json={
            "equipment_id": 1,
            "category_id": 1,
            "technician_id": 1,
            "title": "Unauthorized Test Fault",
            "description": "This fault should not be created.",
            "priority": "ORTA",
        },
    )

    assert response.status_code == 401


def test_admin_can_access_me():
    response = login("admin", "Admin123")

    assert response.status_code == 200

    token = response.json()["access_token"]

    me_response = client.get(
        "/auth/me",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert me_response.status_code == 200
    assert me_response.json()["username"] == "admin"
    assert me_response.json()["role"] == "ADMIN"


def test_invalid_token():
    response = client.get(
        "/faults",
        headers={
            "Authorization": "Bearer invalid-token"
        },
    )

    assert response.status_code == 401