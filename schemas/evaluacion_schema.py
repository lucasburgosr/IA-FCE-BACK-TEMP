from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from schemas.subtema_schema import SubtemaOut


class EvaluacionBase(BaseModel):
    nota: float
    tema: SubtemaOut
    asistente_id: str


class EvaluacionCreate(EvaluacionBase):
    pass


class EvaluacionUpdate(BaseModel):
    nota: Optional[float] = None
    tema_id: Optional[int] = None
    id: Optional[int] = None


class EvaluacionOut(EvaluacionBase):
    evaluacion_id: int
    evaluacion_fecha: datetime

    class Config:
        from_attributes = True
