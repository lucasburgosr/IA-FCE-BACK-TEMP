from pydantic import BaseModel
from typing import List, Optional
from schemas.subtema_schema import TemaOut


class UnidadBase(BaseModel):
    nombre: str
    materia_id: int


class UnidadCreate(UnidadBase):
    pass


class UnidadUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    materia_id: Optional[int] = None


class UnidadOut(UnidadBase):
    unidad_id: int
    subtemas: List[TemaOut] = []

    class Config:
        from_attributes = True
