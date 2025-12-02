from config.db_config import Base
from sqlalchemy import Column, ForeignKey, Integer, String


class Subtema(Base):
    __tablename__ = "subtema"

    subtema_id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    tema_id = Column(Integer, ForeignKey("tema.tema_id"), nullable=False)

    preguntas = relationship("Pregunta", backref="subtema",
                             cascade="all, delete-orphan")
    evaluaciones = relationship(
        "Evaluacion", backref="subtema", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Subtema(tema_id={self.subtema_id}, nombre='{self.nombre}')>"
