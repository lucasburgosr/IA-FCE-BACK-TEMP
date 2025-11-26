from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from schemas.alumno_schema import AlumnoOut
from schemas.profesor_schema import ProfesorOut, ProfesorCreate, ProfesorUpdate
from services.profesor_service import ProfesorService
from config.db_config import get_db
from utils.dependencies import get_current_user

router = APIRouter(
    prefix="/profesores",
    tags=["Profesores"]
)

# --- Inyección de dependencias para el servicio ---
def get_profesor_service(db: AsyncSession = Depends(get_db)) -> ProfesorService:
    return ProfesorService(db)


@router.get("/", response_model=List[ProfesorOut])
async def read_profesores(svc: ProfesorService = Depends(get_profesor_service)):
    return await svc.get_all_profesores()


@router.get("/{profesor_id}", response_model=ProfesorOut)
async def read_profesor(
    profesor_id: int,
    svc: ProfesorService = Depends(get_profesor_service),
    current_user: dict = Depends(get_current_user)
):
    try:
        return await svc.get_profesor_by_id(profesor_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/", response_model=ProfesorOut, status_code=201)
async def create_profesor(
    profesor: ProfesorCreate,
    svc: ProfesorService = Depends(get_profesor_service),
    current_user: dict = Depends(get_current_user)
):
    # Nota: El servicio correspondiente a este método estaba comentado.
    # Asegúrate de que esté activo en ProfesorService si vas a usar este endpoint.
    return await svc.create_profesor(profesor.model_dump())


@router.put("/{profesor_id}", response_model=ProfesorOut)
async def update_profesor(
    profesor_id: int,
    profesor_data: ProfesorUpdate,
    svc: ProfesorService = Depends(get_profesor_service),
    current_user: dict = Depends(get_current_user)
):
    try:
        return await svc.update_profesor(
            profesor_id, profesor_data.model_dump(exclude_unset=True)
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{profesor_id}", status_code=204)
async def delete_profesor(
    profesor_id: int,
    svc: ProfesorService = Depends(get_profesor_service),
    current_user: dict = Depends(get_current_user)
):
    try:
        await svc.delete_profesor(profesor_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{profesor_id}/alumnos", response_model=List[AlumnoOut])
async def get_alumnos_by_profesor(
    profesor_id: int,
    svc: ProfesorService = Depends(get_profesor_service),
    current_user: dict = Depends(get_current_user)
):
    return await svc.listar_estudiantes(profesor_id=profesor_id)