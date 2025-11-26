from config.db_config import Base
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from datetime import datetime, timezone


class Pregunta(Base):
    __tablename__ = "pregunta"

    pregunta_id = Column(Integer, primary_key=True, index=True)
    contenido = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True),
                        default=datetime.now(timezone.utc))
    tema_id = Column(Integer, ForeignKey("tema.tema_id"), nullable=False)
    unidad_id = Column(Integer, ForeignKey("unidad.unidad_id"), nullable=False)
    estudiante_id = Column(Integer, ForeignKey("estudiante.estudiante_id"), nullable=False)
    asistente_id = Column(String(255), ForeignKey(
        "asistente.asistente_id"), nullable=False)

    asistente = relationship("Asistente", back_populates="preguntas")

    def __repr__(self):
        return f"<Pregunta(pregunta_id={self.pregunta_id}, contenido='{self.contenido[:20]}...')>"
