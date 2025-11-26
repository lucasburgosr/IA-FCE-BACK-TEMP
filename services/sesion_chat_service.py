from sqlalchemy.ext.asyncio import AsyncSession
from models.sesion_chat import SesionChat
from repositories.sesion_chat_repository import SessionRepository
from repositories.estudiante_repository import AlumnoRepository

class SesionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = SessionRepository(db)
        self.alumno_repo = AlumnoRepository(db)

    async def start_session(self, estudiante_id: int, thread_id: str) -> SesionChat:
        return await self.repo.create(estudiante_id, thread_id)

    async def end_session(self, sesion_id: int, thread_id: str, estudiante_id: int) -> None:
        # Finaliza la sesión de forma asíncrona
        session = await self.repo.finish(sesion_id)
        if session is None:
            raise ValueError(f"Sesión {sesion_id} no encontrada o ya finalizada")