from sqlalchemy import Column, Integer, DateTime, ForeignKey, Interval, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone, timedelta
from models.usuario import Usuario
from models.estudiante_asistente import estudiante_asistente


class Estudiante(Usuario):
    __tablename__ = "estudiante"

    estudiante_id = Column(Integer, ForeignKey("usuario.id"), primary_key=True)
    last_login = Column(DateTime(timezone=True),
                        default=datetime.now(timezone.utc))
    mensajes_enviados = Column(Integer, default=0, nullable=False)
    tiempo_interaccion = Column(
        Interval, default=lambda: timedelta(), nullable=False)
    """ resumen_ultima_sesion = Column(Text, nullable=True) """

    preguntas = relationship("Pregunta", backref="estudiante",
                             cascade="all, delete-orphan")
    evaluaciones = relationship(
        "Evaluacion", backref="estudiante", cascade="all, delete-orphan")
    asistentes = relationship(
        "Asistente", secondary=estudiante_asistente, backref="estudiante")
    threads = relationship("Thread", backref="estudiante",
                           cascade="all, delete-orphan")
    sesiones = relationship(
        "SesionChat", back_populates="estudiante", cascade="all, delete-orphan")

    __mapper_args__ = {"polymorphic_identity": "estudiante"}

    def __repr__(self):
        return f"<Estudiante(id={self.estudiante_id}, email='{self.email}')>"
