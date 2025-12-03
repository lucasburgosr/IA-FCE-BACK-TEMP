from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
from models.profesor import Profesor
from models.estudiante import Estudiante
from models.asistente import Asistente
from models.materia import Materia
from models.unidad import Unidad
from models.pregunta import Pregunta
from models.evaluacion import Evaluacion
from models.tema import Tema
from models.subtema import Subtema


class ProfesorRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, profesor_id: int) -> Optional[Profesor]:
        query = (
            select(Profesor)
            .options(
                selectinload(Profesor.materia).options(
                    # Si tu relación se llama `asistente` y no `asistentes`, dejala así:
                    selectinload(Materia.asistente),

                    # Materia -> Unidades -> Temas -> Subtemas
                    selectinload(Materia.unidades)
                    .selectinload(Unidad.temas)
                    .selectinload(Tema.subtemas),
                )
            )
            .where(Profesor.profesor_id == profesor_id)
        )
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_all(self) -> List[Profesor]:
        query = (
            select(Profesor)
            .options(
                selectinload(Profesor.materia).selectinload(Materia.unidades)
            )
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def create(self, profesor_data: dict) -> Profesor:
        nuevo_profesor = Profesor(**profesor_data)
        self.db(nuevo_profesor)
        await self.db.commit()
        await self.db.refresh(nuevo_profesor)
        return nuevo_profesor

    async def update(self, profesor: Profesor, update_data: dict) -> Profesor:
        for key, value in update_data.items():
            setattr(profesor, key, value)
        await self.db.commit()
        await self.db.refresh(profesor)
        return profesor

    async def delete(self, profesor: Profesor) -> None:
        await self.db.delete(profesor)
        await self.db.commit()

    
    async def get_estudiantes(self, profesor_id: int) -> List[Estudiante]:
        profesor_result = await self.db.execute(
            select(Profesor).where(Profesor.profesor_id == profesor_id)
        )
        profesor = profesor_result.scalars().first()
        if not profesor:
            return []

        mat_id = profesor.materia_id

        eager_loads_for_alumno_out = (
            selectinload(Estudiante.asistentes),
            selectinload(Estudiante.threads),
            selectinload(Estudiante.preguntas).options(
                selectinload(Pregunta.subtema),
                selectinload(Pregunta.unidad).options(
                    selectinload(Unidad.temas)
                ),
            ),
            selectinload(Estudiante.evaluaciones).options(
                selectinload(Evaluacion.subtema)
                .selectinload(Subtema.tema)
                .selectinload(Tema.unidad)
            ),
        )

        alumnos_query = (
            select(Estudiante)
            .join(Estudiante.asistentes)
            .where(Asistente.materia_id == mat_id)
            .options(*eager_loads_for_alumno_out)
            .distinct()
        )

        result = await self.db.execute(alumnos_query)
        return result.scalars().all()
