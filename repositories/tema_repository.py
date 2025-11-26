from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.tema import Tema


class TemaRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, tema_id: int) -> Optional[Tema]:
        result = await self.db.execute(
            select(Tema).where(Tema.tema_id == tema_id)
        )
        return result.scalars().first()

    async def get_all(self) -> List[Tema]:
        result = await self.db.execute(select(Tema))
        return result.scalars().all()

    async def create(self, subtema_data: dict) -> Tema:
        nuevo_subtema = Tema(**subtema_data)
        self.db.add(nuevo_subtema)
        await self.db.commit()
        await self.db.refresh(nuevo_subtema)
        return nuevo_subtema

    async def update(self, subtema: Tema, update_data: dict) -> Tema:
        for key, value in update_data.items():
            setattr(subtema, key, value)
        await self.db.commit()
        await self.db.refresh(subtema)
        return subtema

    async def delete(self, subtema: Tema) -> None:
        await self.db.delete(subtema)
        await self.db.commit()