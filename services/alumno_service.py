from repositories.estudiante_repository import AlumnoRepository
from typing import Dict, Any, List, Optional
from models.estudiante import Estudiante
from sqlalchemy.ext.asyncio import AsyncSession


class AlumnoService:
    def __init__(self, db: AsyncSession):
        # El servicio ahora recibe una AsyncSession
        self.db = db
        # Y se la pasa al repositorio (que también debe ser asíncrono)
        self.alumno_repo = AlumnoRepository(db)

    async def get_alumno_by_id(self, id: int) -> Estudiante:
        # Se espera el resultado del repositorio
        estudiante = await self.alumno_repo.get_by_id(id)
        if not estudiante:
            raise ValueError(f"Estudiante con id {id} no encontrado")
        return estudiante

    async def get_alumno_by_email(self, email: str) -> Estudiante:
        estudiante = await self.alumno_repo.get_by_email(email)
        if not estudiante:
            # Corregido: El mensaje de error usaba 'id' en lugar de 'email'
            raise ValueError(f"Estudiante con email {email} no encontrado")
        return estudiante

    async def get_all_alumnos(self) -> List[Estudiante]:
        return await self.alumno_repo.get_all()

    async def create_alumno(self, alumno_data: Dict[str, Any]) -> Estudiante:
        # Agregar validaciones para comprobar que el estudiante no esté registrado.
        return await self.alumno_repo.create(alumno_data)

    async def update_alumno(self, id: int, update_data: Dict[str, Any]) -> Estudiante:
        estudiante = await self.alumno_repo.get_by_id(id)
        if not estudiante:
            raise ValueError(f"No se puede actualizar, estudiante con id {id} no encontrado")
        return await self.alumno_repo.update(estudiante, update_data)

    async def delete_alumno(self, id: int) -> None:
        estudiante = await self.alumno_repo.get_by_id(id)
        if not estudiante:
            raise ValueError(f"No se puede eliminar, estudiante con id {id} no encontrado")
        await self.alumno_repo.delete(estudiante)

    async def incrementar_contador_mensajes(self, estudiante_id: int, n: int = 1) -> Estudiante:
        # 1. Obtener el estudiante de forma asíncrona
        estudiante = await self.alumno_repo.get_by_id(estudiante_id)
        if not estudiante:
            raise ValueError(f"Estudiante con id {estudiante_id} no encontrado")

        # 2. La lógica de negocio no cambia
        estudiante.mensajes_enviados += n
        
        # 3. Guardar y refrescar de forma asíncrona
        await self.db.commit()
        await self.db.refresh(estudiante)
        return estudiante