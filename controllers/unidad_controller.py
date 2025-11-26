from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from schemas.unidad_schema import UnidadOut, UnidadCreate, UnidadUpdate
from services.unidad_service import UnidadService
from config.db_config import get_db
from utils.dependencies import get_current_user

router = APIRouter(
    prefix="/unidades",
    tags=["Unidades"]
)

# --- Inyección de dependencias para el servicio ---
def get_unidad_service(db: AsyncSession = Depends(get_db)) -> UnidadService:
    return UnidadService(db)


@router.get("/", response_model=List[UnidadOut])
async def read_unidades(
    svc: UnidadService = Depends(get_unidad_service),
    current_user: dict = Depends(get_current_user)
):
    return await svc.get_all_unidades()


@router.get("/{unidad_id}", response_model=UnidadOut)
async def read_unidad(
    unidad_id: int,
    svc: UnidadService = Depends(get_unidad_service),
    current_user: dict = Depends(get_current_user)
):
    try:
        return await svc.get_unidad_by_id(unidad_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/", response_model=UnidadOut, status_code=201)
async def create_unidad(
    unidad: UnidadCreate,
    svc: UnidadService = Depends(get_unidad_service),
    current_user: dict = Depends(get_current_user)
):
    return await svc.create_unidad(unidad.model_dump())


@router.put("/{unidad_id}", response_model=UnidadOut)
async def update_unidad(
    unidad_id: int,
    unidad_data: UnidadUpdate,
    svc: UnidadService = Depends(get_unidad_service),
    current_user: dict = Depends(get_current_user)
):
    try:
        return await svc.update_unidad(
            unidad_id, unidad_data.model_dump(exclude_unset=True)
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{unidad_id}", status_code=204)
async def delete_unidad(
    unidad_id: int,
    svc: UnidadService = Depends(get_unidad_service),
    current_user: dict = Depends(get_current_user)
):
    try:
        await svc.delete_unidad(unidad_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))