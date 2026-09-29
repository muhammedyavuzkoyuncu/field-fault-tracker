from sqlalchemy import Column, Integer, String, Numeric
from backend.app.database import Base


class Plant(Base):
    __tablename__ = "plants"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False)

    type = Column(String(50))

    province = Column(String(50))

    installed_power_mw = Column(Numeric(10, 2))

    commissioning_year = Column(Integer)

    plant_code = Column(String(50))