from config.db_config import Base
from sqlalchemy import Boolean, Column, Integer, Float, String, DateTime, ForeignKey
from datetime import datetime, timezone


class Evaluacion(Base):
    __tablename__ = "evaluacion"

    evaluacion_id = Column(Integer, primary_key=True, index=True)
    nota = Column(Float, nullable=False)
    evaluacion_fecha = Column(DateTime(timezone=True),
                              default=datetime.now(timezone.utc))
    tema_id = Column(Integer, ForeignKey("tema.tema_id"), nullable=False)
    estudiante_id = Column(Integer, ForeignKey("estudiante.estudiante_id"), nullable=False)
    asistente_id = Column(String, ForeignKey("asistente.asistente_id"), nullable=False)
    pendiente = Column(Boolean, nullable=False, default=True)

    def __repr__(self):
        return f"<Evaluacion(evaluacion_id={self.evaluacion_id}, nota={self.nota})>"
