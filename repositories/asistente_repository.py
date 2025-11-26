from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.asistente import Asistente

class AsistenteRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, asistente_id: str) -> Asistente:
        # return self.db.query(Asistente).filter(Asistente.asistente_id == asistente_id).first()
        result = await self.db.execute(
            select(Asistente).where(Asistente.asistente_id == asistente_id)
        )
        return result.scalars().first()

    async def get_all(self) -> list[Asistente]:
        # return self.db.query(Asistente).all()
        results = await self.db.execute(select(Asistente))
        return results.scalars().all()

    async def create(self, asistente_data: dict) -> Asistente:
        asistente = Asistente(**asistente_data)
        self.db.add(asistente)
        await self.db.commit()
        await self.db.refresh(asistente)
        return asistente

    async def update(self, asistente: Asistente, nueva_data: dict) -> Asistente:
        for key, value in nueva_data.items():
            setattr(asistente, key, value)
        await self.db.commit()
        await self.db.refresh(asistente)
        return asistente

    async def delete(self, asistente: Asistente) -> None:
        await self.db.delete(asistente)
        await self.db.commit()
