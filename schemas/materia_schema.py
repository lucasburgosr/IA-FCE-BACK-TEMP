from pydantic import BaseModel
from typing import List, Optional
from schemas.asistente_schema import AsistenteDBOut
from schemas.unidad_schema import UnidadOut


class MateriaBase(BaseModel):
    nombre: str


class MateriaCreate(MateriaBase):
    pass


class MateriaUpdate(BaseModel):
    nombre: Optional[str] = None


class MateriaOut(MateriaBase):
    materia_id: int
    unidades: List[UnidadOut] = []
    asistente: Optional[AsistenteDBOut] = None

    class Config:
        from_attributes = True
        populate_by_name = True