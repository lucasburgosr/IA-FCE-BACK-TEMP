from pydantic import BaseModel
from typing import Optional


class SubtemaBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    tema_id: int


class SubtemaCreate(SubtemaBase):
    pass


class SubtemaUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    tema_id: Optional[int] = None


class SubtemaOut(SubtemaBase):
    tema_id: int

    class Config:
        from_attributes = True
