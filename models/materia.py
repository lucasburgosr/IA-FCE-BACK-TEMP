from config.db_config import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship


class Materia(Base):
    __tablename__ = "materia"

    materia_id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False, unique=True)

    unidades = relationship("Unidad", backref="materia",
                            cascade="all, delete-orphan")
    profesores = relationship("Profesor", backref="materia")
    asistente = relationship(
        "Asistente", back_populates="materia", cascade="all, delete-orphan", uselist=False)

    def __repr__(self):
        return f"<Materia(materia_id={self.materia_id}, nombre='{self.nombre}')>"
