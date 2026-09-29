from sqlalchemy import Column, Integer, String, ForeignKey
from backend.app.database import Base


class Equipment(Base):
    __tablename__ = "equipment"

    id = Column(Integer, primary_key=True, index=True)

    equipment_code = Column(String(50), unique=True, nullable=False)

    plant_id = Column(Integer, ForeignKey("plants.id"))

    name = Column(String(100), nullable=False)

    type = Column(String(50))

    criticality = Column(String(20))

    plant_code = Column(String(50))