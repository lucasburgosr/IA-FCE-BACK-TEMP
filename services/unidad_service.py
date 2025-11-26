from repositories.unidad_repository import UnidadRepository
from typing import Dict, Any, List
from models.unidad import Unidad
from sqlalchemy.ext.asyncio import AsyncSession

class UnidadService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.unidad_repo = UnidadRepository(db)

    async def get_unidad_by_id(self, unidad_id: int) -> Unidad:
        unidad = await self.unidad_repo.get_by_id(unidad_id)
        if not unidad:
            raise ValueError(f"Unidad con id {unidad_id} no encontrada")
        return unidad

    async def get_all_unidades(self) -> List[Unidad]:
        return await self.unidad_repo.get_all()

    async def create_unidad(self, unidad_data: Dict[str, Any]) -> Unidad:
        # Agregar validaciones aquí si es necesario
        return await self.unidad_repo.create(unidad_data)

    async def update_unidad(self, unidad_id: int, update_data: Dict[str, Any]) -> Unidad:
        unidad = await self.unidad_repo.get_by_id(unidad_id)
        if not unidad:
            raise ValueError(f"No se puede actualizar, unidad con id {unidad_id} no encontrada")
        return await self.unidad_repo.update(unidad, update_data)

    async def delete_unidad(self, unidad_id: int) -> None:
        unidad = await self.unidad_repo.get_by_id(unidad_id)
        if not unidad:
            raise ValueError(f"No se puede eliminar, unidad con id {unidad_id} no encontrada")
        await self.unidad_repo.delete(unidad)