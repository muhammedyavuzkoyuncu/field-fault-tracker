from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


# =====================================================
# AUTH HEADER
# =====================================================

def get_auth_headers():

    login_response = client.post(
        "/auth/login",
        json={
            "username": "admin",
            "password": "Admin123"
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }


# =====================================================
# HEALTH
# =====================================================

def test_health():

    response = client.get("/health")

    assert response.status_code == 200

    assert response.json() == {
        "status": "ok"
    }


# =====================================================
# DATABASE
# =====================================================

def test_db_connection():

    headers = get_auth_headers()

    response = client.get(
        "/db-test",
        headers=headers
    )

    assert response.status_code == 200

    data = response.json()

    assert data["database"] == "connected"

    assert "plant_count" in data


# =====================================================
# PLANTS
# =====================================================

def test_get_plants():

    headers = get_auth_headers()

    response = client.get(
        "/plants",
        headers=headers
    )

    assert response.status_code == 200

    assert isinstance(
        response.json(),
        list
    )


# =====================================================
# EQUIPMENT
# =====================================================

def test_get_equipment():

    headers = get_auth_headers()

    response = client.get(
        "/equipment",
        headers=headers
    )

    assert response.status_code == 200

    assert isinstance(
        response.json(),
        list
    )


# =====================================================
# TECHNICIANS
# =====================================================

def test_get_technicians():

    headers = get_auth_headers()

    response = client.get(
        "/technicians",
        headers=headers
    )

    assert response.status_code == 200

    assert isinstance(
        response.json(),
        list
    )


# =====================================================
# FAULT CATEGORIES
# =====================================================

def test_get_fault_categories():

    headers = get_auth_headers()

    response = client.get(
        "/fault-categories",
        headers=headers
    )

    assert response.status_code == 200

    assert isinstance(
        response.json(),
        list
    )


# =====================================================
# FAULT CRUD
# =====================================================

def test_fault_crud():

    headers = get_auth_headers()

    create_response = client.post(
        "/faults",
        headers=headers,
        json={
            "equipment_id": 1,
            "category_id": 1,
            "technician_id": 1,
            "title": "Automated Test Fault",
            "description": "This fault was created by an automated test.",
            "priority": "ORTA",
        },
    )

    assert create_response.status_code == 200

    create_data = create_response.json()

    assert create_data["message"] == "Fault created"

    assert "fault_id" in create_data

    fault_id = create_data["fault_id"]

    # -------------------------------------------------
    # GET
    # -------------------------------------------------

    get_response = client.get(
        f"/faults/{fault_id}",
        headers=headers
    )

    assert get_response.status_code == 200

    get_data = get_response.json()

    assert get_data["id"] == fault_id

    assert get_data["title"] == "Automated Test Fault"

    # Gereksiz teknik alanlar dönmemeli.
    assert "client_uuid" not in get_data

    assert "equipment_id" not in get_data

    assert "category_id" not in get_data

    assert "technician_id" not in get_data

    assert "updated_at" not in get_data

    # -------------------------------------------------
    # UPDATE
    # -------------------------------------------------

    update_response = client.put(
        f"/faults/{fault_id}",
        headers=headers,
        json={
            "title": "Updated Automated Test Fault",
            "description": "This fault was updated by an automated test.",
            "status": "DEVAM_EDIYOR",
            "priority": "YUKSEK",
            "equipment_id": 1,
            "category_id": 1,
            "technician_id": 1,
        },
    )

    assert update_response.status_code == 200

    # -------------------------------------------------
    # DELETE
    # -------------------------------------------------

    delete_response = client.delete(
        f"/faults/{fault_id}",
        headers=headers
    )

    assert delete_response.status_code == 200

    delete_data = delete_response.json()

    assert delete_data["message"] == "Fault deleted"

    assert delete_data["fault_id"] == fault_id


# =====================================================
# FAULT NOT FOUND
# =====================================================

def test_get_fault_not_found():

    headers = get_auth_headers()

    response = client.get(
        "/faults/999999",
        headers=headers
    )

    assert response.status_code == 200

    assert response.json() == {
        "message": "Fault not found"
    }


def test_delete_fault_not_found():

    headers = get_auth_headers()

    response = client.delete(
        "/faults/999999",
        headers=headers
    )

    assert response.status_code == 200

    assert response.json() == {
        "message": "Fault not found"
    }


# =====================================================
# GET ALL FAULTS
# =====================================================

def test_get_all_faults():

    headers = get_auth_headers()

    response = client.get(
        "/faults",
        headers=headers
    )

    assert response.status_code == 200

    assert isinstance(
        response.json(),
        list
    )


# =====================================================
# UPDATE NOT FOUND
# =====================================================

def test_update_fault_not_found():

    headers = get_auth_headers()

    response = client.put(
        "/faults/999999",
        headers=headers,
        json={
            "title": "Non Existing Fault",
            "description": "This fault does not exist.",
            "status": "ACIK",
            "priority": "ORTA",
            "equipment_id": 1,
            "category_id": 1,
            "technician_id": 1,
        },
    )

    assert response.status_code == 200

    assert response.json() == {
        "message": "Fault not found"
    }


# =====================================================
# UNAUTHORIZED ACCESS
# =====================================================

def test_faults_without_token():

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


def test_db_test_without_token():

    response = client.get("/db-test")

    assert response.status_code == 401


def test_plants_without_token():

    response = client.get("/plants")

    assert response.status_code == 401


def test_equipment_without_token():

    response = client.get("/equipment")

    assert response.status_code == 401


def test_technicians_without_token():

    response = client.get("/technicians")

    assert response.status_code == 401


def test_categories_without_token():

    response = client.get("/fault-categories")

    assert response.status_code == 401