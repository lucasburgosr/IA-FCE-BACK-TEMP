from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from schemas.alumno_schema import AlumnoOut, AlumnoCreate, AlumnoUpdate
from services.alumno_service import AlumnoService
from config.db_config import get_db
from utils.dependencies import get_current_user

router = APIRouter(
    prefix="/alumnos",
    tags=["Alumnos"]
)

# --- Inyección de dependencias para el servicio ---
def get_alumno_service(db: AsyncSession = Depends(get_db)) -> AlumnoService:
    return AlumnoService(db)


@router.get("/", response_model=List[AlumnoOut])
async def read_alumnos(
    svc: AlumnoService = Depends(get_alumno_service),
    current_user: dict = Depends(get_current_user)
):
    return await svc.get_all_alumnos()


@router.get("/{id}", response_model=AlumnoOut)
async def read_alumno(
    id: int,
    svc: AlumnoService = Depends(get_alumno_service),
    current_user: dict = Depends(get_current_user)
):
    try:
        return await svc.get_alumno_by_id(id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/", response_model=AlumnoOut, status_code=201)
async def create_alumno(
    estudiante: AlumnoCreate,
    svc: AlumnoService = Depends(get_alumno_service),
    current_user: dict = Depends(get_current_user)
):
    return await svc.create_alumno(estudiante.model_dump())


@router.put("/{id}", response_model=AlumnoOut)
async def update_alumno(
    id: int,
    alumno_data: AlumnoUpdate,
    svc: AlumnoService = Depends(get_alumno_service),
    current_user: dict = Depends(get_current_user)
):
    try:
        return await svc.update_alumno(id, alumno_data.model_dump(exclude_unset=True))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{id}", status_code=204)
async def delete_alumno(
    id: int,
    svc: AlumnoService = Depends(get_alumno_service),
    current_user: dict = Depends(get_current_user)
):
    try:
        await svc.delete_alumno(id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))