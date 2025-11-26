from repositories.profesor_repository import ProfesorRepository
from typing import Dict, Any, List
from models.estudiante import Estudiante
from models.profesor import Profesor
from sqlalchemy.ext.asyncio import AsyncSession


class ProfesorService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.profesor_repo = ProfesorRepository(db)

    async def get_profesor_by_id(self, profesor_id: int) -> Profesor:
        profesor = await self.profesor_repo.get_by_id(profesor_id)
        if not profesor:
            raise ValueError(f"Profesor con id {profesor_id} no encontrado")
        return profesor

    async def get_all_profesores(self) -> List[Profesor]:
        return await self.profesor_repo.get_all()

    async def update_profesor(self, profesor_id: int, update_data: Dict[str, Any]) -> Profesor:
        profesor = await self.profesor_repo.get_by_id(profesor_id)
        if not profesor:
            raise ValueError(f"No se puede actualizar, profesor con id {profesor_id} no encontrado")
        return await self.profesor_repo.update(profesor, update_data)

    async def delete_profesor(self, profesor_id: int) -> None:
        profesor = await self.profesor_repo.get_by_id(profesor_id)
        if not profesor:
            raise ValueError(f"No se puede eliminar, profesor con id {profesor_id} no encontrado")
        await self.profesor_repo.delete(profesor)

    async def listar_estudiantes(self, profesor_id: int) -> List[Estudiante]:
        alumnos = await self.profesor_repo.get_estudiantes(profesor_id)
        return alumnos