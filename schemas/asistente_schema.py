from pydantic import BaseModel, Field
from typing import Optional

# En estos schemas resolvemos un problema del naming de variables:

# - en la base de datos, la columna que contiene el nombre del asistente se llama "nombre"
# - en la API, el nombre viene en la propiedad "name"

# Estos schemas se encargan de traducir el nombre de la variable tanto para los datos de salida como de entrada,
# lo que nos evita tener que renombrar columnas en la base de datos y en repositorios, servicios y controladores.


class AsistenteBase(BaseModel):

    nombre: str = Field(..., alias="name")
    instructions: str

    class Config:
        from_attributes = True
        # permite usar "nombre" internamente y "name" externamente
        populate_by_name = True


class AsistenteCreate(AsistenteBase):
    pass


class AsistenteUpdate(BaseModel):
    nombre: Optional[str] = Field(None, alias="name")
    instructions: Optional[str] = None

    class Config:
        from_attributes = True
        populate_by_name = True


class AsistenteDBOut(AsistenteBase):
    asistente_id: str
    nombre: str
    materia_id: int


class AsistenteOpenAIOut(AsistenteBase):
    asistente_id: str
    name: str

    class Config:
        from_attributes = True
        populate_by_name = True
