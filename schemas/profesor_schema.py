from pydantic import BaseModel, EmailStr
from typing import Optional
from schemas.materia_schema import MateriaOut
from pydantic import BaseModel, EmailStr
from typing import Optional


class ProfesorBase(BaseModel):
    email: EmailStr
    materia: MateriaOut
    contrasena: str


class ProfesorCreate(ProfesorBase):
    pass


class ProfesorUpdate(BaseModel):
    email: Optional[EmailStr] = None
    contrasena: Optional[str] = None
    materia_id: int = None


class ProfesorOut(BaseModel):
    profesor_id: int
    email: EmailStr
    materia: MateriaOut

    class Config:
        from_attributes = True
        populate_by_name = True
