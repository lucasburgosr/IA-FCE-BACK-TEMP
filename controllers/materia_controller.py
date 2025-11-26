from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from schemas.materia_schema import MateriaOut, MateriaCreate, MateriaUpdate
from services.materia_service import MateriaService
from config.db_config import get_db
from utils.dependencies import get_current_user

router = APIRouter(
    prefix="/materias",
    tags=["Materias"]
)

# --- Inyección de dependencias para el servicio ---
def get_materia_service(db: AsyncSession = Depends(get_db)) -> MateriaService:
    return MateriaService(db)


@router.get("/", response_model=List[MateriaOut])
async def read_materias(
    svc: MateriaService = Depends(get_materia_service),
    current_user: dict = Depends(get_current_user)
):
    return await svc.get_all_materias()


@router.get("/{materia_id}", response_model=MateriaOut)
async def read_materia(
    materia_id: int,
    svc: MateriaService = Depends(get_materia_service),
    current_user: dict = Depends(get_current_user)
):
    try:
        return await svc.get_materia_by_id(materia_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/", response_model=MateriaOut, status_code=201)
async def create_materia(
    materia: MateriaCreate,
    svc: MateriaService = Depends(get_materia_service),
    current_user: dict = Depends(get_current_user)
):
    return await svc.create_materia(materia.model_dump())


@router.put("/{materia_id}", response_model=MateriaOut)
async def update_materia(
    materia_id: int,
    materia_data: MateriaUpdate,
    svc: MateriaService = Depends(get_materia_service),
    current_user: dict = Depends(get_current_user)
):
    try:
        return await svc.update_materia(
            materia_id, materia_data.model_dump(exclude_unset=True)
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{materia_id}", status_code=204)
async def delete_materia(
    materia_id: int,
    svc: MateriaService = Depends(get_materia_service),
    current_user: dict = Depends(get_current_user)
):
    try:
        await svc.delete_materia(materia_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))