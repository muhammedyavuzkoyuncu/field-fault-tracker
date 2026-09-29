from sqlalchemy import Column, Integer, String
from backend.app.database import Base


class Technician(Base):
    __tablename__ = "technicians"

    id = Column(Integer, primary_key=True, index=True)

    full_name = Column(String(100), nullable=False)

    specialization = Column(String(100))

    technician_code = Column(String(50))

    main_plant_code = Column(String(50))