from sqlalchemy.ext.asyncio import AsyncSession
from models.evaluacion import Evaluacion
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from models.subtema import Subtema
from models.tema import Tema
from typing import List

class EvaluacionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, evaluacion_id: int) -> Evaluacion:
        result = await self.db.execute(
            select(Evaluacion).where(Evaluacion.evaluacion_id == evaluacion_id)
        )
        return result.scalars().first()

    async def get_all(self) -> list[Evaluacion]:
        results = await self.db.execute(select(Evaluacion))
        return results.scalars().all()

    async def get_by_alumno(self, estudiante_id: int) -> List[Evaluacion]:
        query = (
            select(Evaluacion)
            .options(
                selectinload(Evaluacion.subtema).options(
                    selectinload(Subtema.tema)
                )
            )
            .where(Evaluacion.estudiante_id == estudiante_id)
        )
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_by_asistente(self, asistente_id: str) -> List[Evaluacion]:
        query = (
            select(Evaluacion)
            .options(
                selectinload(Evaluacion.subtema)
                .selectinload(Subtema.tema)
                .selectinload(Tema.unidad)
            )
            .where(Evaluacion.asistente_id == asistente_id)
        )
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def create(self, evaluacion_data: dict) -> Evaluacion:
        nueva_evaluacion = Evaluacion(**evaluacion_data)
        self.db.add(nueva_evaluacion)
        await self.db.commit()
        await self.db.refresh(nueva_evaluacion)
        return nueva_evaluacion

    async def update(self, evaluacion: Evaluacion, update_data: dict) -> Evaluacion:
        for key, value in update_data.items():
            setattr(evaluacion, key, value)
        await self.db.commit()
        await self.db.refresh(evaluacion)
        return evaluacion

    async def delete(self, evaluacion: Evaluacion) -> None:
        await self.db.delete(evaluacion)
        await self.db.commit()
