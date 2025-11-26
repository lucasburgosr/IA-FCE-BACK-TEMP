from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.unidad import Unidad


class UnidadRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, unidad_id: int) -> Optional[Unidad]:
        result = await self.db.execute(
            select(Unidad).where(Unidad.unidad_id == unidad_id)
        )
        return result.scalars().first()

    async def get_all(self) -> List[Unidad]:
        result = await self.db.execute(select(Unidad))
        return result.scalars().all()

    async def create(self, unidad_data: dict) -> Unidad:
        nueva_unidad = Unidad(**unidad_data)
        self.db.add(nueva_unidad)
        await self.db.commit()
        await self.db.refresh(nueva_unidad)
        return nueva_unidad

    async def update(self, unidad: Unidad, update_data: dict) -> Unidad:
        for key, value in update_data.items():
            setattr(unidad, key, value)
        await self.db.commit()
        await self.db.refresh(unidad)
        return unidad

    async def delete(self, unidad: Unidad) -> None:
        await self.db.delete(unidad)
        await self.db.commit()