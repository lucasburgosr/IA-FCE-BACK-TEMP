from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from models.materia import Materia
from models.unidad import Unidad
from models.tema import Tema
from sqlalchemy import select


class MateriaRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, materia_id: int) -> Materia:
        query = (
            select(Materia)
            .options(
                selectinload(Materia.unidades)
                .selectinload(Unidad.temas)
                .selectinload(Tema.subtemas),

                selectinload(Materia.asistente)
            )
            .where(Materia.materia_id == materia_id)
        )

        result = await self.db.execute(query)
        return result.scalars().first()
    
    async def get_by_nombre(self, nombre: str) -> Materia:
        query = (
            select(Materia)
            .options(
                selectinload(Materia.unidades).selectinload(Unidad.subtemas),
                selectinload(Materia.asistente)
            )
            .where(Materia.nombre == nombre)
        )

        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_all(self) -> list[Materia]:
        results = await self.db.execute(select(Materia))
        return results.scalars().all()

    async def create(self, materia_data: dict) -> Materia:
        nueva_materia = Materia(**materia_data)
        self.db.add(nueva_materia)
        await self.db.commit()
        await self.db.refresh(nueva_materia)
        return nueva_materia

    async def update(self, materia: Materia, update_data: dict) -> Materia:
        for key, value in update_data.items():
            setattr(materia, key, value)
        await self.db.commit()
        await self.db.refresh(materia)
        return materia

    async def delete(self, materia: Materia) -> None:
        await self.db.delete(materia)
        await self.db.commit()
