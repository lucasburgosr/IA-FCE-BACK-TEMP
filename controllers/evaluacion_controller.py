from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from schemas.evaluacion_schema import EvaluacionOut, EvaluacionCreate, EvaluacionUpdate
from services.evaluacion_service import EvaluacionService
from config.db_config import get_db
from utils.dependencies import get_current_user

router = APIRouter(
    prefix="/evaluaciones",
    tags=["Evaluaciones"]
)

# --- Inyección de dependencias para el servicio ---
def get_evaluacion_service(db: AsyncSession = Depends(get_db)) -> EvaluacionService:
    return EvaluacionService(db)


@router.get("/", response_model=List[EvaluacionOut])
async def read_evaluaciones(
    svc: EvaluacionService = Depends(get_evaluacion_service),
    current_user: dict = Depends(get_current_user)
):
    return await svc.get_all_evaluaciones()


@router.get("/{evaluacion_id}", response_model=EvaluacionOut)
async def read_evaluacion(
    evaluacion_id: int,
    svc: EvaluacionService = Depends(get_evaluacion_service),
    current_user: dict = Depends(get_current_user)
):
    try:
        return await svc.get_evaluacion_by_id(evaluacion_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/estudiante/{estudiante_id}", response_model=List[EvaluacionOut])
async def read_evaluacion_by_alumno(
    estudiante_id: int,
    svc: EvaluacionService = Depends(get_evaluacion_service),
    current_user: dict = Depends(get_current_user)
):
    try:
        return await svc.get_evaluaciones_by_alumno(estudiante_id=estudiante_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/asistente/{asistente_id}", response_model=List[EvaluacionOut])
async def read_evaluaciones_by_asistente(
    asistente_id: str,
    svc: EvaluacionService = Depends(get_evaluacion_service),
    current_user: dict = Depends(get_current_user)
):
    try:
        return await svc.get_evaluaciones_by_asistente(asistente_id=asistente_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/", response_model=EvaluacionOut, status_code=201)
async def create_evaluacion(
    evaluacion: EvaluacionCreate,
    svc: EvaluacionService = Depends(get_evaluacion_service),
    current_user: dict = Depends(get_current_user)
):
    return await svc.create_evaluacion(evaluacion.model_dump())


@router.put("/{evaluacion_id}", response_model=EvaluacionOut)
async def update_evaluacion(
    evaluacion_id: int,
    evaluacion_data: EvaluacionUpdate,
    svc: EvaluacionService = Depends(get_evaluacion_service),
    current_user: dict = Depends(get_current_user)
):
    try:
        return await svc.update_evaluacion(evaluacion_id, evaluacion_data.model_dump(exclude_unset=True))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{evaluacion_id}", status_code=204)
async def delete_evaluacion(
    evaluacion_id: int,
    svc: EvaluacionService = Depends(get_evaluacion_service),
    current_user: dict = Depends(get_current_user)
):
    try:
        await svc.delete_evaluacion(evaluacion_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))