from config.db_config import Base
from sqlalchemy import Column, ForeignKey, Integer, String
from models.tema import Tema
from sqlalchemy.orm import relationship

class Subtema(Base):
    __tablename__ = "subtema"

    subtema_id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    tema_id = Column(Integer, ForeignKey("tema.tema_id"), nullable=False)

    tema = relationship("Tema", back_populates="subtemas")

    preguntas = relationship("Pregunta", backref="subtema",
                             cascade="all, delete-orphan")
    
    evaluaciones = relationship(
        "Evaluacion",
        back_populates="subtema",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Subtema(tema_id={self.subtema_id}, nombre='{self.nombre}')>"
