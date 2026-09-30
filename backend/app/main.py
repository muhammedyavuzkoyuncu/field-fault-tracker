from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import text

from backend.app.database import engine


app = FastAPI(title="Field Fault Tracker API")


# --------------------------------------------------
# HEALTH
# --------------------------------------------------

@app.get("/health")
def health():
    return {"status": "ok"}


# --------------------------------------------------
# DATABASE TEST
# --------------------------------------------------

@app.get("/db-test")
def db_test():
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT COUNT(*) FROM plants")
        )
        count = result.scalar()

    return {
        "database": "connected",
        "plant_count": count
    }


# --------------------------------------------------
# PLANTS
# --------------------------------------------------

@app.get("/plants")
def get_plants():
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


# --------------------------------------------------
# CREATE FAULT
# --------------------------------------------------

class FaultCreate(BaseModel):
    equipment_id: int
    category_id: int
    technician_id: int
    title: str
    description: str
    priority: str = "ORTA"


@app.post("/faults")
def create_fault(fault: FaultCreate):
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
                "equipment_id": fault.equipment_id,
                "category_id": fault.category_id,
                "technician_id": fault.technician_id,
                "title": fault.title,
                "description": fault.description,
                "priority": fault.priority,
            }
        )

        fault_id = result.scalar()
        conn.commit()

    return {
        "message": "Fault created",
        "fault_id": fault_id
    }


# --------------------------------------------------
# GET ALL FAULTS
# --------------------------------------------------

@app.get("/faults")
def get_faults():
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


# --------------------------------------------------
# GET SINGLE FAULT
# --------------------------------------------------

@app.get("/faults/{fault_id}")
def get_fault(fault_id: int):
    with engine.connect() as conn:
        result = conn.execute(
            text("""
                SELECT
                    f.id,
                    f.client_uuid,
                    f.title,
                    f.description,
                    f.status,
                    f.priority,
                    f.created_at,
                    f.updated_at,

                    f.equipment_id,
                    e.name AS equipment_name,

                    f.category_id,
                    c.name AS category_name,

                    f.technician_id,
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


# --------------------------------------------------
# UPDATE FAULT
# --------------------------------------------------

class FaultUpdate(BaseModel):
    title: str
    description: str
    status: str
    priority: str
    equipment_id: int
    category_id: int
    technician_id: int


@app.put("/faults/{fault_id}")
def update_fault(fault_id: int, fault: FaultUpdate):
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
# --------------------------------------------------
# DELETE FAULT
# --------------------------------------------------

@app.delete("/faults/{fault_id}")
def delete_fault(fault_id: int):
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
# --------------------------------------------------
# EQUIPMENT
# --------------------------------------------------

@app.get("/equipment")
def get_equipment():
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
# --------------------------------------------------
# TECHNICIANS
# --------------------------------------------------

@app.get("/technicians")
def get_technicians():
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
# --------------------------------------------------
# FAULT CATEGORIES
# --------------------------------------------------

@app.get("/fault-categories")
def get_fault_categories():
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