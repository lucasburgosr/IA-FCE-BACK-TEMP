from repositories.pregunta_repository import PreguntaRepository
from typing import Dict, Any, List
from models.pregunta import Pregunta
from sqlalchemy.ext.asyncio import AsyncSession
from services.vector_store_service import VectorService


class PreguntaService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.pregunta_repo = PreguntaRepository(db)

    async def get_pregunta_by_id(self, pregunta_id: int) -> Pregunta:
        pregunta = await self.pregunta_repo.get_by_id(pregunta_id)
        if not pregunta:
            raise ValueError(f"Pregunta con id {pregunta_id} no encontrada")
        return pregunta

    async def get_pregunta_by_asistente(self, asistente_id: str) -> List[Pregunta]:
        return await self.pregunta_repo.get_by_asistente(asistente_id=asistente_id)
    
    async def get_ultima_pregunta_by_estudiante(self, estudiante_id: int) -> Pregunta:
        return await self.pregunta_repo.get_ultima_pregunta_by_estudiante(estudiante_id=estudiante_id)

    async def get_all_preguntas(self) -> List[Pregunta]:
        return await self.pregunta_repo.get_all()

    async def create_pregunta(self, pregunta_data: Dict[str, Any]) -> Pregunta:
        return await self.pregunta_repo.create(pregunta_data)

    async def update_pregunta(self, pregunta_id: int, update_data: Dict[str, Any]) -> Pregunta:
        pregunta = await self.pregunta_repo.get_by_id(pregunta_id)
        if not pregunta:
            raise ValueError(f"No se puede actualizar, pregunta con id {pregunta_id} no encontrada")
        return await self.pregunta_repo.update(pregunta, update_data)

    async def delete_pregunta(self, pregunta_id: int) -> None:
        pregunta = await self.pregunta_repo.get_by_id(pregunta_id)
        if not pregunta:
            raise ValueError(f"No se puede eliminar, pregunta con id {pregunta_id} no encontrada")
        await self.pregunta_repo.delete(pregunta)

    async def insertar_y_clasificar_pregunta(self, texto: str, vector_store_id: str, estudiante_id: str, asistente_id: str):
        vector_service = VectorService(self.db)
        tema_id, unidad_id = await vector_service.clasificar_consulta(
            texto=texto, vector_store_id=vector_store_id, estudiante_id=estudiante_id
        )

        pregunta_data = {
            "contenido": texto, "tema_id": tema_id, "unidad_id": unidad_id,
            "estudiante_id": estudiante_id, "asistente_id": asistente_id
        }
        pregunta = await self.create_pregunta(pregunta_data=pregunta_data)
        return pregunta