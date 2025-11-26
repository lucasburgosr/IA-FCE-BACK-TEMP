from typing import Literal, Optional
from pydantic import BaseModel, field_validator
from datetime import datetime


class ParteTexto(BaseModel):
    type: Literal["text"] = "text"
    text: str

class ParteImagen(BaseModel):
    type: Literal["image"] = "image"
    data_url: str          # data:image/png;base64,AAAB...

ContentPart = ParteTexto | ParteImagen

class MensajeBase(BaseModel):
    texto: Optional[str] = None
    rol: str


class MensajeCreate(MensajeBase):
    id: str


class MensajeOut(MensajeBase):
    id: str
    fecha: datetime
    partes: list[ContentPart]

    @field_validator("fecha", mode="before")
    def convertir_timestamp(cls, value):
        if isinstance(value, int):
            return datetime.fromtimestamp(value)
        return value
