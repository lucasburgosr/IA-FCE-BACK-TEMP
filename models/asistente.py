from config.db_config import Base
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from models.thread_asistente import thread_asistente


class Asistente(Base):
    __tablename__ = "asistente"

    asistente_id = Column(String(100), primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    instructions = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True),
                        default=datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True),
                        default=datetime.now(timezone.utc))
    materia_id = Column(Integer, ForeignKey(
        "materia.materia_id"), nullable=False)
    vs_temas_id = Column(String(50), nullable=False)
    vs_evaluaciones_id = Column(String(50), nullable=False)
    evaluador_id = Column(String(50), nullable=True)

    materia = relationship("Materia", back_populates="asistente")
    threads = relationship(
        "Thread", secondary=thread_asistente, back_populates="asistentes")
    preguntas = relationship("Pregunta", back_populates="asistente")

    def __repr__(self):
        return f"<Asistente(asistente_id={self.asistente_id}, name='{self.name}')>"
