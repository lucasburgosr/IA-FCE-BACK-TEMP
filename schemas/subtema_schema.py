from pydantic import BaseModel
from typing import Optional


class TemaBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    unidad_id: int


class TemaCreate(TemaBase):
    pass


class TemaUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    unidad_id: Optional[int] = None


class TemaOut(TemaBase):
    tema_id: int

    class Config:
        from_attributes = True
