from repositories.materia_repository import MateriaRepository
from typing import Dict, Any, List
from models.materia import Materia
from sqlalchemy.ext.asyncio import AsyncSession


class MateriaService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.materia_repo = MateriaRepository(db)

    async def get_materia_by_id(self, materia_id: int) -> Materia:
        materia = await self.materia_repo.get_by_id(materia_id)
        if not materia:
            raise ValueError(f"Materia con id {materia_id} no encontrada")
        return materia

    async def get_materia_by_nombre(self, nombre: str) -> Materia:
        materia = await self.materia_repo.get_by_nombre(nombre=nombre)
        if not materia:
            raise ValueError(f"Materia con nombre {nombre} no encontrada")
        return materia

    async def get_all_materias(self) -> List[Materia]:
        return await self.materia_repo.get_all()

    async def create_materia(self, materia_data: Dict[str, Any]) -> Materia:
        return await self.materia_repo.create(materia_data)

    async def update_materia(self, materia_id: int, update_data: Dict[str, Any]) -> Materia:
        materia = await self.materia_repo.get_by_id(materia_id)
        if not materia:
            raise ValueError(f"No se puede actualizar, materia con id {materia_id} no encontrada")
        return await self.materia_repo.update(materia, update_data)

    async def delete_materia(self, materia_id: int) -> None:
        materia = await self.materia_repo.get_by_id(materia_id)
        if not materia:
            raise ValueError(f"No se puede eliminar, materia con id {materia_id} no encontrada")
        await self.materia_repo.delete(materia)