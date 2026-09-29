from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from backend.app.database import Base


class Fault(Base):
    __tablename__ = "faults"

    id = Column(Integer, primary_key=True, index=True)

    client_uuid = Column(UUID(as_uuid=True))

    equipment_id = Column(
        Integer,
        ForeignKey("equipment.id")
    )

    category_id = Column(
        Integer,
        ForeignKey("fault_categories.id")
    )

    technician_id = Column(
        Integer,
        ForeignKey("technicians.id")
    )

    title = Column(String(200), nullable=False)

    description = Column(Text)

    status = Column(
        String(20),
        default="ACIK"
    )

    priority = Column(
        String(20),
        default="ORTA"
    )

    created_at = Column(
        DateTime,
        server_default=func.current_timestamp()
    )

    updated_at = Column(
        DateTime,
        server_default=func.current_timestamp()
    )