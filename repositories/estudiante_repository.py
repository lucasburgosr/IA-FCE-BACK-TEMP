from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from models.estudiante import Estudiante
from models.pregunta import Pregunta
from models.evaluacion import Evaluacion
from models.unidad import Unidad
from models.tema import Tema
from models.subtema import Subtema


class AlumnoRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.eager_loads = (
            selectinload(Estudiante.asistentes),
            selectinload(Estudiante.threads),

            # Estudiante -> Preguntas
            selectinload(Estudiante.preguntas).options(
                # Pregunta -> Subtema -> Tema -> Unidad (si te interesa llegar a unidad)
                selectinload(Pregunta.subtema)
                .selectinload(Subtema.tema)
                .selectinload(Tema.unidad),

                # Pregunta -> Unidad -> Temas -> Subtemas
                selectinload(Pregunta.unidad)
                .selectinload(Unidad.temas)
                .selectinload(Tema.subtemas),
            ),

            # Estudiante -> Evaluaciones -> Subtema -> Tema -> Unidad
            selectinload(Estudiante.evaluaciones).options(
                selectinload(Evaluacion.subtema)
                .selectinload(Subtema.tema)
                .selectinload(Tema.unidad)
            ),
        )

    async def get_by_id(self, id: int) -> Optional[Estudiante]:
        query = (
            select(Estudiante)
            .options(*self.eager_loads)
            .where(Estudiante.id == id)
        )
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_all(self) -> List[Estudiante]:
        query = select(Estudiante).options(*self.eager_loads)
        results = await self.db.execute(query)
        return results.scalars().all()

    async def get_by_email(self, email: str) -> Optional[Estudiante]:
        query = (
            select(Estudiante)
            .options(*self.eager_loads)
            .where(Estudiante.email == email)
        )
        result = await self.db.execute(query)
        return result.scalars().first()

    async def create(self, alumno_data: dict) -> Estudiante:
        print("Intentamos el registro en create")
        nuevo_alumno = Estudiante(**alumno_data)
        self.db.add(nuevo_alumno)
        await self.db.commit()
        await self.db.refresh(nuevo_alumno)
        return nuevo_alumno

    async def update(self, estudiante: Estudiante, update_data: dict) -> Estudiante:
        for key, value in update_data.items():
            setattr(estudiante, key, value)
        await self.db.commit()
        await self.db.refresh(estudiante)
        return estudiante

    async def delete(self, estudiante: Estudiante) -> None:
        await self.db.delete(estudiante)
        await self.db.commit()
