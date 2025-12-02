from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from schemas.subtema_schema import SubtemaOut
from schemas.unidad_schema import UnidadOut


class PreguntaBase(BaseModel):
    contenido: str
    subtema: SubtemaOut
    unidad: UnidadOut


class PreguntaCreate(PreguntaBase):
    asistente_id: str


class PreguntaUpdate(BaseModel):
    contenido: Optional[str] = None
    subtema_id: Optional[int] = None
    id: Optional[int] = None


class PreguntaOut(PreguntaBase):
    pregunta_id: int
    created_at: datetime
    asistente_id: str

    class Config:
        from_attributes = True
