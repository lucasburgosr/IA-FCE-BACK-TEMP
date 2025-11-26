from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from schemas.pregunta_schema import PreguntaOut, PreguntaCreate, PreguntaUpdate
from services.pregunta_service import PreguntaService
from config.db_config import get_db
from utils.dependencies import get_current_user

router = APIRouter(
    prefix="/preguntas",
    tags=["Preguntas"]
)

# --- Inyección de dependencias para el servicio ---
def get_pregunta_service(db: AsyncSession = Depends(get_db)) -> PreguntaService:
    return PreguntaService(db)


@router.get("/", response_model=List[PreguntaOut])
async def read_preguntas(
    svc: PreguntaService = Depends(get_pregunta_service),
    current_user: dict = Depends(get_current_user)
):
    return await svc.get_all_preguntas()


# 1. Ruta corregida para evitar conflicto
@router.get("/asistente/{asistente_id}", response_model=List[PreguntaOut])
async def read_preguntas_by_asistente(
    asistente_id: str,
    svc: PreguntaService = Depends(get_pregunta_service),
    current_user: dict = Depends(get_current_user)
):
    return await svc.get_pregunta_by_asistente(asistente_id=asistente_id)


@router.get("/{pregunta_id}", response_model=PreguntaOut)
async def read_pregunta(
    pregunta_id: int,
    svc: PreguntaService = Depends(get_pregunta_service),
    current_user: dict = Depends(get_current_user)
):
    try:
        return await svc.get_pregunta_by_id(pregunta_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/", response_model=PreguntaOut, status_code=201)
async def create_pregunta(
    pregunta: PreguntaCreate,
    svc: PreguntaService = Depends(get_pregunta_service),
    current_user: dict = Depends(get_current_user)
):
    return await svc.create_pregunta(pregunta.model_dump())


@router.put("/{pregunta_id}", response_model=PreguntaOut)
async def update_pregunta(
    pregunta_id: int,
    pregunta_data: PreguntaUpdate,
    svc: PreguntaService = Depends(get_pregunta_service),
    current_user: dict = Depends(get_current_user)
):
    try:
        return await svc.update_pregunta(
            pregunta_id, pregunta_data.model_dump(exclude_unset=True)
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{pregunta_id}", status_code=204)
async def delete_pregunta(
    pregunta_id: int,
    svc: PreguntaService = Depends(get_pregunta_service),
    current_user: dict = Depends(get_current_user)
):
    try:
        await svc.delete_pregunta(pregunta_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))