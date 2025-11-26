from repositories.tema_repository import TemaRepository
from typing import Dict, Any, List
from models.tema import Tema
from sqlalchemy.ext.asyncio import AsyncSession


class SubtemaService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.subtema_repo = TemaRepository(db)

    async def get_subtema_by_id(self, tema_id: int) -> Tema:
        subtema = await self.subtema_repo.get_by_id(tema_id)
        if not subtema:
            raise ValueError(f"Tema con id {tema_id} no encontrado")
        return subtema

    async def get_all_subtemas(self) -> List[Tema]:
        return await self.subtema_repo.get_all()

    async def create_subtema(self, subtema_data: Dict[str, Any]) -> Tema:
        # Agregar validaciones aquí si es necesario
        return await self.subtema_repo.create(subtema_data)

    async def update_subtema(self, tema_id: int, update_data: Dict[str, Any]) -> Tema:
        subtema = await self.subtema_repo.get_by_id(tema_id)
        if not subtema:
            raise ValueError(f"No se puede actualizar, tema con id {tema_id} no encontrado")
        return await self.subtema_repo.update(subtema, update_data)

    async def delete_subtema(self, tema_id: int) -> None:
        subtema = await self.subtema_repo.get_by_id(tema_id)
        if not subtema:
            raise ValueError(f"No se puede eliminar, tema con id {tema_id} no encontrado")
        await self.subtema_repo.delete(subtema)