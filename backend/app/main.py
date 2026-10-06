from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends
from fastapi import HTTPException

from pydantic import BaseModel, EmailStr
from sqlalchemy import text

from backend.app.auth.routes import (
    router as auth_router,
    get_current_user,
    require_admin,
)

from backend.app.auth.security import hash_password

from backend.app.database import engine


app = FastAPI(title="Field Fault Tracker API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =====================================================
# AUTHENTICATION ROUTER
# =====================================================

app.include_router(auth_router)


# =====================================================
# HEALTH
# =====================================================

@app.get("/health")
def health():

    return {
        "status": "ok"
    }


# =====================================================
# DATABASE TEST
# =====================================================

@app.get("/db-test")
def db_test(
    current_user=Depends(require_admin)
):

    with engine.connect() as conn:

        result = conn.execute(
            text("SELECT COUNT(*) FROM plants")
        )

        count = result.scalar()

    return {
        "database": "connected",
        "plant_count": count
    }


# =====================================================
# PLANTS
# =====================================================

class PlantCreate(BaseModel):

    name: str
    type: str | None = None
    province: str | None = None
    installed_power_mw: float | None = None
    commissioning_year: int | None = None
    plant_code: str | None = None


class PlantUpdate(BaseModel):

    name: str
    type: str | None = None
    province: str | None = None
    installed_power_mw: float | None = None
    commissioning_year: int | None = None
    plant_code: str | None = None


# -----------------------------------------------------
# GET PLANTS
# -----------------------------------------------------

@app.get("/plants")
def get_plants(
    current_user=Depends(get_current_user)
):

    with engine.connect() as conn:

        result = conn.execute(
            text("""
                SELECT
                    id,
                    name,
                    type,
                    province,
                    installed_power_mw,
                    commissioning_year,
                    plant_code

                FROM plants

                ORDER BY id
            """)
        )

        rows = result.mappings().all()

    return rows


# -----------------------------------------------------
# CREATE PLANT - ADMIN ONLY
# -----------------------------------------------------

@app.post("/plants")
def create_plant(
    data: PlantCreate,
    current_user=Depends(require_admin)
):

    with engine.connect() as conn:

        # Plant code varsa duplicate kontrolü
        if data.plant_code:

            existing = conn.execute(
                text("""
                    SELECT id
                    FROM plants
                    WHERE plant_code = :plant_code
                """),
                {
                    "plant_code": data.plant_code
                }
            ).fetchone()

            if existing:

                raise HTTPException(
                    status_code=409,
                    detail="Plant code already exists."
                )

        result = conn.execute(
            text("""
                INSERT INTO plants
                (
                    name,
                    type,
                    province,
                    installed_power_mw,
                    commissioning_year,
                    plant_code
                )

                VALUES
                (
                    :name,
                    :type,
                    :province,
                    :installed_power_mw,
                    :commissioning_year,
                    :plant_code
                )

                RETURNING
                    id,
                    name,
                    type,
                    province,
                    installed_power_mw,
                    commissioning_year,
                    plant_code
            """),
            {
                "name": data.name,
                "type": data.type,
                "province": data.province,
                "installed_power_mw": data.installed_power_mw,
                "commissioning_year": data.commissioning_year,
                "plant_code": data.plant_code
            }
        )

        plant = result.mappings().first()

        conn.commit()

    return {
        "message": "Plant created",
        "plant": plant
    }


# -----------------------------------------------------
# UPDATE PLANT - ADMIN ONLY
# -----------------------------------------------------

@app.put("/plants/{plant_id}")
def update_plant(
    plant_id: int,
    data: PlantUpdate,
    current_user=Depends(require_admin)
):

    with engine.connect() as conn:

        existing = conn.execute(
            text("""
                SELECT id
                FROM plants
                WHERE id = :plant_id
            """),
            {
                "plant_id": plant_id
            }
        ).fetchone()

        if existing is None:

            return {
                "message": "Plant not found"
            }

        # Aynı plant_code başka kayıtta kullanılıyor mu?
        if data.plant_code:

            duplicate = conn.execute(
                text("""
                    SELECT id
                    FROM plants
                    WHERE plant_code = :plant_code
                    AND id != :plant_id
                """),
                {
                    "plant_code": data.plant_code,
                    "plant_id": plant_id
                }
            ).fetchone()

            if duplicate:

                raise HTTPException(
                    status_code=409,
                    detail="Plant code already exists."
                )

        result = conn.execute(
            text("""
                UPDATE plants

                SET
                    name = :name,
                    type = :type,
                    province = :province,
                    installed_power_mw = :installed_power_mw,
                    commissioning_year = :commissioning_year,
                    plant_code = :plant_code

                WHERE id = :plant_id

                RETURNING
                    id,
                    name,
                    type,
                    province,
                    installed_power_mw,
                    commissioning_year,
                    plant_code
            """),
            {
                "plant_id": plant_id,
                "name": data.name,
                "type": data.type,
                "province": data.province,
                "installed_power_mw": data.installed_power_mw,
                "commissioning_year": data.commissioning_year,
                "plant_code": data.plant_code
            }
        )

        plant = result.mappings().first()

        conn.commit()

    return {
        "message": "Plant updated",
        "plant": plant
    }


# -----------------------------------------------------
# DELETE PLANT - ADMIN ONLY
# -----------------------------------------------------

@app.delete("/plants/{plant_id}")
def delete_plant(
    plant_id: int,
    current_user=Depends(require_admin)
):

    with engine.connect() as conn:

        result = conn.execute(
            text("""
                DELETE FROM plants

                WHERE id = :plant_id

                RETURNING
                    id,
                    name,
                    plant_code
            """),
            {
                "plant_id": plant_id
            }
        )

        plant = result.mappings().first()

        if plant is None:

            return {
                "message": "Plant not found"
            }

        conn.commit()

    return {
        "message": "Plant deleted",
        "plant": plant
    }


# =====================================================
# CREATE FAULT
# =====================================================

class FaultCreate(BaseModel):

    equipment_id: int
    category_id: int
    technician_id: int
    title: str
    description: str
    priority: str = "ORTA"


@app.post("/faults")
def create_fault(
    data: FaultCreate,
    current_user=Depends(get_current_user)
):

    with engine.connect() as conn:

        result = conn.execute(
            text("""
                INSERT INTO faults
                (
                    equipment_id,
                    category_id,
                    technician_id,
                    title,
                    description,
                    priority
                )

                VALUES
                (
                    :equipment_id,
                    :category_id,
                    :technician_id,
                    :title,
                    :description,
                    :priority
                )

                RETURNING id
            """),
            {
                "equipment_id": data.equipment_id,
                "category_id": data.category_id,
                "technician_id": data.technician_id,
                "title": data.title,
                "description": data.description,
                "priority": data.priority,
            }
        )

        fault_id = result.scalar()

        conn.commit()

    return {
        "message": "Fault created",
        "fault_id": fault_id
    }


# =====================================================
# GET ALL FAULTS
# =====================================================

@app.get("/faults")
def get_faults(
    current_user=Depends(get_current_user)
):

    with engine.connect() as conn:

        result = conn.execute(
            text("""
                SELECT
                    f.id,
                    f.title,
                    f.description,
                    f.status,
                    f.priority,
                    f.created_at,

                    e.name AS equipment_name,

                    t.full_name AS technician_name,

                    c.name AS category_name

                FROM faults f

                LEFT JOIN equipment e
                    ON f.equipment_id = e.id

                LEFT JOIN technicians t
                    ON f.technician_id = t.id

                LEFT JOIN fault_categories c
                    ON f.category_id = c.id

                ORDER BY f.id DESC
            """)
        )

        rows = result.mappings().all()

    return rows


# =====================================================
# GET SINGLE FAULT
# =====================================================

@app.get("/faults/{fault_id}")
def get_fault(
    fault_id: int,
    current_user=Depends(get_current_user)
):

    with engine.connect() as conn:

        result = conn.execute(
            text("""
                SELECT
                    f.id,
                    f.title,
                    f.description,
                    f.status,
                    f.priority,
                    f.created_at,

                    e.name AS equipment_name,

                    c.name AS category_name,

                    t.full_name AS technician_name

                FROM faults f

                LEFT JOIN equipment e
                    ON f.equipment_id = e.id

                LEFT JOIN fault_categories c
                    ON f.category_id = c.id

                LEFT JOIN technicians t
                    ON f.technician_id = t.id

                WHERE f.id = :fault_id
            """),
            {
                "fault_id": fault_id
            }
        )

        row = result.mappings().first()

    if row is None:

        return {
            "message": "Fault not found"
        }

    return row


# =====================================================
# UPDATE FAULT
# =====================================================

class FaultUpdate(BaseModel):

    title: str
    description: str
    status: str
    priority: str
    equipment_id: int
    category_id: int
    technician_id: int


@app.put("/faults/{fault_id}")
def update_fault(
    fault_id: int,
    fault: FaultUpdate,
    current_user=Depends(get_current_user)
):

    with engine.connect() as conn:

        result = conn.execute(
            text("""
                UPDATE faults

                SET
                    title = :title,
                    description = :description,
                    status = :status,
                    priority = :priority,
                    equipment_id = :equipment_id,
                    category_id = :category_id,
                    technician_id = :technician_id,
                    updated_at = CURRENT_TIMESTAMP

                WHERE id = :fault_id

                RETURNING id
            """),
            {
                "fault_id": fault_id,
                "title": fault.title,
                "description": fault.description,
                "status": fault.status,
                "priority": fault.priority,
                "equipment_id": fault.equipment_id,
                "category_id": fault.category_id,
                "technician_id": fault.technician_id,
            }
        )

        updated_id = result.scalar()

        if updated_id is None:

            return {
                "message": "Fault not found"
            }

        conn.commit()

    return {
        "message": "Fault updated",
        "fault_id": updated_id
    }


# =====================================================
# DELETE FAULT - ADMIN ONLY
# =====================================================

@app.delete("/faults/{fault_id}")
def delete_fault(
    fault_id: int,
    current_user=Depends(require_admin)
):

    with engine.connect() as conn:

        result = conn.execute(
            text("""
                DELETE FROM faults

                WHERE id = :fault_id

                RETURNING id
            """),
            {
                "fault_id": fault_id
            }
        )

        deleted_id = result.scalar()

        if deleted_id is None:

            return {
                "message": "Fault not found"
            }

        conn.commit()

    return {
        "message": "Fault deleted",
        "fault_id": deleted_id
    }


# =====================================================
# EQUIPMENT
# =====================================================

class EquipmentCreate(BaseModel):

    equipment_code: str
    name: str
    type: str | None = None
    criticality: str | None = None
    plant_id: int | None = None
    plant_code: str | None = None


class EquipmentUpdate(BaseModel):

    equipment_code: str
    name: str
    type: str | None = None
    criticality: str | None = None
    plant_id: int | None = None
    plant_code: str | None = None


@app.get("/equipment")
def get_equipment(
    current_user=Depends(get_current_user)
):

    with engine.connect() as conn:

        result = conn.execute(
            text("""
                SELECT
                    e.id,
                    e.equipment_code,
                    e.name,
                    e.type,
                    e.criticality,
                    e.plant_id,
                    p.name AS plant_name,
                    e.plant_code

                FROM equipment e

                LEFT JOIN plants p
                    ON e.plant_id = p.id

                ORDER BY e.id
            """)
        )

        rows = result.mappings().all()

    return rows


@app.post("/equipment")
def create_equipment(
    data: EquipmentCreate,
    current_user=Depends(require_admin)
):

    with engine.connect() as conn:

        existing = conn.execute(
            text("""
                SELECT id
                FROM equipment
                WHERE equipment_code = :equipment_code
            """),
            {
                "equipment_code": data.equipment_code
            }
        ).fetchone()

        if existing:

            raise HTTPException(
                status_code=409,
                detail="Equipment code already exists."
            )

        result = conn.execute(
            text("""
                INSERT INTO equipment
                (
                    equipment_code,
                    name,
                    type,
                    criticality,
                    plant_id,
                    plant_code
                )

                VALUES
                (
                    :equipment_code,
                    :name,
                    :type,
                    :criticality,
                    :plant_id,
                    :plant_code
                )

                RETURNING
                    id,
                    equipment_code,
                    name,
                    type,
                    criticality,
                    plant_id,
                    plant_code
            """),
            {
                "equipment_code": data.equipment_code,
                "name": data.name,
                "type": data.type,
                "criticality": data.criticality,
                "plant_id": data.plant_id,
                "plant_code": data.plant_code
            }
        )

        equipment = result.mappings().first()

        conn.commit()

    return {
        "message": "Equipment created",
        "equipment": equipment
    }


@app.put("/equipment/{equipment_id}")
def update_equipment(
    equipment_id: int,
    data: EquipmentUpdate,
    current_user=Depends(require_admin)
):

    with engine.connect() as conn:

        existing = conn.execute(
            text("""
                SELECT id
                FROM equipment
                WHERE id = :equipment_id
            """),
            {
                "equipment_id": equipment_id
            }
        ).fetchone()

        if existing is None:

            return {
                "message": "Equipment not found"
            }

        duplicate = conn.execute(
            text("""
                SELECT id
                FROM equipment

                WHERE equipment_code = :equipment_code
                AND id != :equipment_id
            """),
            {
                "equipment_code": data.equipment_code,
                "equipment_id": equipment_id
            }
        ).fetchone()

        if duplicate:

            raise HTTPException(
                status_code=409,
                detail="Equipment code already exists."
            )

        result = conn.execute(
            text("""
                UPDATE equipment

                SET
                    equipment_code = :equipment_code,
                    name = :name,
                    type = :type,
                    criticality = :criticality,
                    plant_id = :plant_id,
                    plant_code = :plant_code

                WHERE id = :equipment_id

                RETURNING
                    id,
                    equipment_code,
                    name,
                    type,
                    criticality,
                    plant_id,
                    plant_code
            """),
            {
                "equipment_id": equipment_id,
                "equipment_code": data.equipment_code,
                "name": data.name,
                "type": data.type,
                "criticality": data.criticality,
                "plant_id": data.plant_id,
                "plant_code": data.plant_code
            }
        )

        equipment = result.mappings().first()

        conn.commit()

    return {
        "message": "Equipment updated",
        "equipment": equipment
    }


@app.delete("/equipment/{equipment_id}")
def delete_equipment(
    equipment_id: int,
    current_user=Depends(require_admin)
):

    with engine.connect() as conn:

        result = conn.execute(
            text("""
                DELETE FROM equipment

                WHERE id = :equipment_id

                RETURNING
                    id,
                    equipment_code,
                    name
            """),
            {
                "equipment_id": equipment_id
            }
        )

        equipment = result.mappings().first()

        if equipment is None:

            return {
                "message": "Equipment not found"
            }

        conn.commit()

    return {
        "message": "Equipment deleted",
        "equipment": equipment
    }


# =====================================================
# TECHNICIANS
# =====================================================

@app.get("/technicians")
def get_technicians(
    current_user=Depends(get_current_user)
):

    with engine.connect() as conn:

        result = conn.execute(
            text("""
                SELECT
                    id,
                    full_name,
                    specialization,
                    technician_code,
                    main_plant_code

                FROM technicians

                ORDER BY id
            """)
        )

        rows = result.mappings().all()

    return rows


# =====================================================
# FAULT CATEGORIES
# =====================================================

@app.get("/fault-categories")
def get_fault_categories(
    current_user=Depends(get_current_user)
):

    with engine.connect() as conn:

        result = conn.execute(
            text("""
                SELECT
                    id,
                    category_code,
                    name,
                    description

                FROM fault_categories

                ORDER BY id
            """)
        )

        rows = result.mappings().all()

    return rows


# =====================================================
# USER MODELLERİ
# =====================================================

class UserCreate(BaseModel):

    username: str
    email: EmailStr
    password: str
    role: str = "TECHNICIAN"


class UserRoleUpdate(BaseModel):

    role: str


# =====================================================
# GET USERS - ADMIN ONLY
# =====================================================

@app.get("/users")
def get_users(
    current_user=Depends(require_admin)
):

    with engine.connect() as conn:

        result = conn.execute(
            text("""
                SELECT
                    id,
                    username,
                    email,
                    role,
                    created_at

                FROM users

                ORDER BY id
            """)
        )

        rows = result.mappings().all()

    return rows


# =====================================================
# CREATE USER - ADMIN ONLY
# =====================================================

@app.post("/users")
def create_user(
    data: UserCreate,
    current_user=Depends(require_admin)
):

    if len(data.password) < 8:

        raise HTTPException(
            status_code=400,
            detail="Password must be at least 8 characters."
        )

    if data.role not in {
        "ADMIN",
        "TECHNICIAN"
    }:

        raise HTTPException(
            status_code=400,
            detail="Invalid role."
        )

    password_hash = hash_password(
        data.password
    )

    with engine.connect() as conn:

        existing_user = conn.execute(
            text("""
                SELECT id
                FROM users

                WHERE username = :username
                OR email = :email
            """),
            {
                "username": data.username,
                "email": data.email
            }
        ).fetchone()

        if existing_user:

            raise HTTPException(
                status_code=409,
                detail="Username or email already exists."
            )

        result = conn.execute(
            text("""
                INSERT INTO users
                (
                    username,
                    email,
                    password_hash,
                    role
                )

                VALUES
                (
                    :username,
                    :email,
                    :password_hash,
                    :role
                )

                RETURNING
                    id,
                    username,
                    email,
                    role,
                    created_at
            """),
            {
                "username": data.username,
                "email": data.email,
                "password_hash": password_hash,
                "role": data.role
            }
        )

        user = result.mappings().first()

        conn.commit()

    return {
        "message": "User created",
        "user": user
    }


# =====================================================
# UPDATE USER ROLE - ADMIN ONLY
# =====================================================

@app.put("/users/{user_id}/role")
def update_user_role(
    user_id: int,
    data: UserRoleUpdate,
    current_user=Depends(require_admin)
):

    if data.role not in {
        "ADMIN",
        "TECHNICIAN"
    }:

        raise HTTPException(
            status_code=400,
            detail="Invalid role."
        )

    with engine.connect() as conn:

        target_user = conn.execute(
            text("""
                SELECT
                    id,
                    username,
                    role

                FROM users

                WHERE id = :user_id
            """),
            {
                "user_id": user_id
            }
        ).mappings().first()

        if target_user is None:

            return {
                "message": "User not found"
            }

        if (
            target_user["id"] == current_user["id"]
            and data.role != "ADMIN"
        ):

            raise HTTPException(
                status_code=400,
                detail="You cannot remove your own admin role."
            )

        if (
            target_user["role"] == "ADMIN"
            and data.role == "TECHNICIAN"
        ):

            admin_count = conn.execute(
                text("""
                    SELECT COUNT(*)
                    FROM users
                    WHERE role = 'ADMIN'
                """)
            ).scalar()

            if admin_count <= 1:

                raise HTTPException(
                    status_code=400,
                    detail="At least one admin user must remain."
                )

        result = conn.execute(
            text("""
                UPDATE users

                SET role = :role

                WHERE id = :user_id

                RETURNING
                    id,
                    username,
                    email,
                    role
            """),
            {
                "user_id": user_id,
                "role": data.role
            }
        )

        user = result.mappings().first()

        conn.commit()

    return {
        "message": "User role updated",
        "user": user
    }


# =====================================================
# DELETE USER - ADMIN ONLY
# =====================================================

@app.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    current_user=Depends(require_admin)
):

    if user_id == current_user["id"]:

        raise HTTPException(
            status_code=400,
            detail="You cannot delete your own account."
        )

    with engine.connect() as conn:

        target_user = conn.execute(
            text("""
                SELECT
                    id,
                    username,
                    role

                FROM users

                WHERE id = :user_id
            """),
            {
                "user_id": user_id
            }
        ).mappings().first()

        if target_user is None:

            return {
                "message": "User not found"
            }

        if target_user["role"] == "ADMIN":

            admin_count = conn.execute(
                text("""
                    SELECT COUNT(*)
                    FROM users
                    WHERE role = 'ADMIN'
                """)
            ).scalar()

            if admin_count <= 1:

                raise HTTPException(
                    status_code=400,
                    detail="At least one admin user must remain."
                )

        result = conn.execute(
            text("""
                DELETE FROM users

                WHERE id = :user_id

                RETURNING
                    id,
                    username,
                    email,
                    role
            """),
            {
                "user_id": user_id
            }
        )

        deleted_user = result.mappings().first()

        conn.commit()

    return {
        "message": "User deleted",
        "user": deleted_user
    }