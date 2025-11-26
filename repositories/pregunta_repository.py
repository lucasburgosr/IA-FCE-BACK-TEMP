from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
from models.pregunta import Pregunta
from models.tema import Tema
from models.unidad import Unidad


class PreguntaRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, pregunta_id: int) -> Pregunta:
        result = await self.db.execute(
            select(Pregunta).where(Pregunta.pregunta_id == pregunta_id)
        )
        return result.scalars().first()

    async def get_all(self) -> list[Pregunta]:
        results = await self.db.execute(select(Pregunta))
        return results.scalars().all()

    async def create(self, pregunta_data: dict) -> Pregunta:
        nueva_pregunta = Pregunta(**pregunta_data)
        self.db.add(nueva_pregunta)
        await self.db.commit()
        await self.db.refresh(nueva_pregunta)
        return nueva_pregunta

    async def get_ultima_pregunta_by_estudiante(self, estudiante_id: int) -> Pregunta:
        result = await self.db.execute(
            select(Pregunta)
            .where(Pregunta.estudiante_id == estudiante_id)
            .order_by(Pregunta.pregunta_id.desc())
        )
        return result.scalars().first()

    async def update(self, pregunta: Pregunta, update_data: dict) -> Pregunta:
        for key, value in update_data.items():
            setattr(pregunta, key, value)
        await self.db.commit()
        await self.db.refresh(pregunta)
        return pregunta

    async def delete(self, pregunta: Pregunta) -> None:
        await self.db.delete(pregunta)
        await self.db.commit()

    async def get_by_asistente(self, asistente_id: str) -> List[Pregunta]:
        query = (
            select(Pregunta)
            .options(
                selectinload(Pregunta.tema).options(
                    selectinload(Tema.unidad)
                ),
                selectinload(Pregunta.unidad).options(
                    selectinload(Unidad.subtemas)
                )
            )
            .where(Pregunta.asistente_id == asistente_id)
        )
        result = await self.db.execute(query)
        return result.scalars().all()