from pydantic import BaseModel, Field
from typing import Optional


class ThreadBase(BaseModel):
    title: Optional[str] = None


class ThreadCreate(ThreadBase):
    estudiante_id: int = Field(..., alias="alumnoId")
    asistente_id: str = Field(..., alias="asistenteId")


class ThreadUpdate(BaseModel):
    title: Optional[str] = None
    id: Optional[int] = None


class ThreadOut(ThreadBase):
    id: str

    class Config:
        from_attributes = True
