from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.thread import Thread
from repositories.asistente_repository import AsistenteRepository

class ThreadRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, id: str) -> Optional[Thread]:
        result = await self.db.execute(
            select(Thread).where(Thread.id == id)
        )
        return result.scalars().first()

    async def get_by_alumno(self, estudiante_id: int) -> Optional[Thread]:
        result = await self.db.execute(
            select(Thread).where(Thread.estudiante_id == estudiante_id)
        )
        return result.scalars().first()

    async def get_all(self) -> List[Thread]:
        result = await self.db.execute(select(Thread))
        return result.scalars().all()

    async def create(self, thread_data: dict, asistente_id: str) -> Thread:
        nuevo_thread = Thread(**thread_data)
        print(thread_data)
        asistente = await AsistenteRepository.get_by_id(self=self, asistente_id=asistente_id)
        nuevo_thread.asistentes.append(asistente)
        self.db.add(nuevo_thread)
        await self.db.commit()
        await self.db.refresh(nuevo_thread)
        return nuevo_thread

    async def update(self, thread: Thread, update_data: dict) -> Thread:
        for key, value in update_data.items():
            setattr(thread, key, value)
        await self.db.commit()
        await self.db.refresh(thread)
        return thread

    async def delete(self, thread: Thread) -> None:
        await self.db.delete(thread)
        await self.db.commit()