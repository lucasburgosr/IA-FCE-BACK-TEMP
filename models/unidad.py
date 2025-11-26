from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from config.db_config import Base


class Unidad(Base):
    __tablename__ = "unidad"

    unidad_id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    materia_id = Column(Integer, ForeignKey(
        "materia.materia_id"), nullable=False)

    subtemas = relationship("Tema", backref="unidad",
                            cascade="all, delete-orphan")
    preguntas = relationship("Pregunta", backref="unidad")

    def __repr__(self):
        return f"<Unidad(unidad_id={self.unidad_id}, nombre='{self.nombre}')>"
