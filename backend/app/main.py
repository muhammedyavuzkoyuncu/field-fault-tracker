from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import text

from backend.app.database import engine

app = FastAPI(title="Field Fault Tracker API")


@app.get("/health")
def health():
    return {"status": "ok"}


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