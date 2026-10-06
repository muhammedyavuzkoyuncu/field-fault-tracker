import uuid

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


def get_admin_headers():
    response = login("admin", "Admin123")

    assert response.status_code == 200

    token = response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }


def test_admin_can_list_users():
    headers = get_admin_headers()

    response = client.get(
        "/users",
        headers=headers
    )

    assert response.status_code == 200

    users = response.json()

    assert isinstance(users, list)
    assert len(users) >= 1


def test_admin_can_create_user():
    headers = get_admin_headers()

    unique_id = uuid.uuid4().hex[:8]

    username = f"test_technician_{unique_id}"
    email = f"test_technician_{unique_id}@test.com"

    response = client.post(
        "/users",
        headers=headers,
        json={
            "username": username,
            "email": email,
            "password": "Test1234",
            "role": "TECHNICIAN",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "User created"
    assert data["user"]["username"] == username
    assert data["user"]["email"] == email
    assert data["user"]["role"] == "TECHNICIAN"


def test_admin_can_update_user_role():
    headers = get_admin_headers()

    unique_id = uuid.uuid4().hex[:8]

    username = f"role_test_user_{unique_id}"
    email = f"role_test_user_{unique_id}@test.com"

    create_response = client.post(
        "/users",
        headers=headers,
        json={
            "username": username,
            "email": email,
            "password": "Test1234",
            "role": "TECHNICIAN",
        },
    )

    assert create_response.status_code == 200

    user_id = create_response.json()["user"]["id"]

    update_response = client.put(
        f"/users/{user_id}/role",
        headers=headers,
        json={
            "role": "ADMIN"
        },
    )

    assert update_response.status_code == 200

    data = update_response.json()

    assert data["message"] == "User role updated"
    assert data["user"]["id"] == user_id
    assert data["user"]["role"] == "ADMIN"

    # Test kullanıcısını temizle
    delete_response = client.delete(
        f"/users/{user_id}",
        headers=headers
    )

    assert delete_response.status_code == 200


def test_admin_can_delete_user():
    headers = get_admin_headers()

    unique_id = uuid.uuid4().hex[:8]

    username = f"delete_test_user_{unique_id}"
    email = f"delete_test_user_{unique_id}@test.com"

    create_response = client.post(
        "/users",
        headers=headers,
        json={
            "username": username,
            "email": email,
            "password": "Test1234",
            "role": "TECHNICIAN",
        },
    )

    assert create_response.status_code == 200

    user_id = create_response.json()["user"]["id"]

    delete_response = client.delete(
        f"/users/{user_id}",
        headers=headers
    )

    assert delete_response.status_code == 200

    data = delete_response.json()

    assert data["message"] == "User deleted"
    assert data["user"]["id"] == user_id


def test_unauthenticated_user_cannot_list_users():
    response = client.get("/users")

    assert response.status_code == 401


def test_unauthenticated_user_cannot_create_user():
    response = client.post(
        "/users",
        json={
            "username": "unauthorized_user",
            "email": "unauthorized@test.com",
            "password": "Test1234",
            "role": "TECHNICIAN",
        },
    )

    assert response.status_code == 401


def test_admin_cannot_delete_own_account():
    headers = get_admin_headers()

    me_response = client.get(
        "/auth/me",
        headers=headers
    )

    assert me_response.status_code == 200

    admin_id = me_response.json()["id"]

    response = client.delete(
        f"/users/{admin_id}",
        headers=headers
    )

    assert response.status_code == 400

    assert response.json()["detail"] == (
        "You cannot delete your own account."
    )