from config.db_config import Base
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime, timezone

class Run(Base):

    __tablename__ = "run"

    run_id = Column(String(255), primary_key=True)
    status =  Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    last_error = Column(String(255), nullable=True)