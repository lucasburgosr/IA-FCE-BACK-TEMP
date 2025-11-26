from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.sesion_chat import SesionChat
from sqlalchemy.orm import selectinload

class SessionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, sesion_id: int) -> Optional[SesionChat]:
        result = await self.db.execute(
            select(SesionChat).where(SesionChat.sesion_id == sesion_id)
        )
        return result.scalars().first()

    async def create(self, estudiante_id: int, thread_id: str) -> SesionChat:
        session = SesionChat(
            estudiante_id=estudiante_id,
            thread_id=thread_id,
            iniciada_en=datetime.now(timezone.utc)
        )
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def finish(self, sesion_id: int) -> Optional[SesionChat]:
        query = (
            select(SesionChat)
            .options(selectinload(SesionChat.estudiante))
            .where(SesionChat.sesion_id == sesion_id)
        )
        result = await self.db.execute(query)
        session = result.scalars().one_or_none()

        if not session or session.finalizada_en is not None:
            return None

        session.finalizada_en = datetime.now(timezone.utc)
        delta = session.finalizada_en - session.iniciada_en
        session.estudiante.tiempo_interaccion += delta

        await self.db.commit()
        await self.db.refresh(session)
        return session