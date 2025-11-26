from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime
from typing import Optional, List
from datetime import timedelta
from schemas.asistente_schema import AsistenteDBOut
from schemas.evaluacion_schema import EvaluacionOut
from schemas.pregunta_schema import PreguntaOut
from schemas.thread_schema import ThreadOut

# Schema base con los campos comunes
class AlumnoBase(BaseModel):
    email: EmailStr
    
class AlumnoCreate(AlumnoBase):
    pass

class AlumnoUpdate(BaseModel):
    email: Optional[EmailStr] = None
    firebase_uid: Optional[str] = None
    contrasena: Optional[str] = None
    
class AlumnoOut(AlumnoBase):
    id: int
    nombres: str
    apellido: str
    last_login: datetime | None
    mensajes_enviados: int = 0
    tiempo_interaccion: str
    asistentes: List[AsistenteDBOut] = []
    preguntas: List[PreguntaOut] = []
    evaluaciones: List[EvaluacionOut] = []
    threads: List[ThreadOut] = []
    resumen_ultima_sesion: Optional[str] = None
    
    class Config:
        from_attributes = True
    
    @field_validator("tiempo_interaccion", mode="before")
    def format_tiempo_interaccion(cls, v):
        if isinstance(v, timedelta):
            total_seconds = int(v.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            return f"{hours:02}:{minutes:02}:{seconds:02}"
        return v