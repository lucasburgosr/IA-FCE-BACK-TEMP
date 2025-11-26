from sqlalchemy import Table, Column, ForeignKey, String
from config.db_config import Base

thread_asistente = Table(
    "thread_asistente",
    Base.metadata,
    Column("thread_id", String, ForeignKey("thread.id"), primary_key=True),
    Column("asistente_id", String, ForeignKey(
        "asistente.asistente_id"), primary_key=True)
)
