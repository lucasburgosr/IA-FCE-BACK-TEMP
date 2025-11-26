from sqlalchemy import Column, Integer, ForeignKey
from models.usuario import Usuario


class Profesor(Usuario):
    __tablename__ = "profesor"

    profesor_id = Column(Integer, ForeignKey("usuario.id"), primary_key=True)
    materia_id = Column(Integer, ForeignKey(
        "materia.materia_id"), nullable=False)

    __mapper_args__ = {"polymorphic_identity": "profesor"}

    def __repr__(self):
        return f"<Profesor(profesor_id={self.profesor_id}, email='{self.email}')>"
