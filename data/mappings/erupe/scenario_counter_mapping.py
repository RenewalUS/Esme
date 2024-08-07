"""Table mappings module"""
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from ..base_mapping import Base

class ScenarioCounter(Base):
    """Scenario Counter table object"""
    __tablename__ = "scenario_counter"
    id: Mapped[int] = mapped_column(primary_key=True)
