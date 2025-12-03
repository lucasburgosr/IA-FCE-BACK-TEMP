from config.db_config import Base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship


class Tema(Base):
    __tablename__ = "tema"

    tema_id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    unidad_id = Column(Integer, ForeignKey("unidad.unidad_id"), nullable=False)

    subtemas = relationship("Subtema", back_populates="tema",
                            cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Subtema(tema_id={self.tema_id}, nombre='{self.nombre}')>"
