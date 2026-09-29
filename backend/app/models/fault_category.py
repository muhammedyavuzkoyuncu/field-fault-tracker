from sqlalchemy import Column, Integer, String, Text
from backend.app.database import Base


class FaultCategory(Base):
    __tablename__ = "fault_categories"

    id = Column(Integer, primary_key=True, index=True)

    category_code = Column(String(50), unique=True, nullable=False)

    name = Column(String(100), nullable=False)

    description = Column(Text)