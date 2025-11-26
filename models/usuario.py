from sqlalchemy import Column, String, Integer, DateTime
from config.db_config import Base
from datetime import datetime, timezone


class Usuario(Base):
    __tablename__ = "usuario"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), nullable=False, unique=True)
    # contrasena = Column(String(255), nullable=True)
    nombres = Column(String(255), nullable=False)
    apellido = Column(String(255), nullable=False)
    nro_documento = Column(Integer, nullable=False)
    # firebase_uid = Column(String(255), nullable=True, unique=True)
    created_at = Column(DateTime(timezone=True),
                        default=datetime.now(timezone.utc))

    type = Column(String(50))

    __mapper_args__ = {
        "polymorphic_identity": "usuario", "polymorphic_on": type}

    def __repr__(self):
        return f"<Estudiante(id={self.id}, email='{self.email}', grado='{self.type}')>"