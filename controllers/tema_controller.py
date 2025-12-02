from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from schemas.subtema_schema import SubtemaOut, SubtemaCreate, SubtemaUpdate
from services.subtema_service import SubtemaService
from config.db_config import get_db
from utils.dependencies import get_current_user

router = APIRouter(
    prefix="/subtemas",
    tags=["Subtemas"]
)

# --- Inyección de dependencias para el servicio ---
def get_subtema_service(db: AsyncSession = Depends(get_db)) -> SubtemaService:
    return SubtemaService(db)


@router.get("/", response_model=List[SubtemaOut])
async def read_subtemas(
    svc: SubtemaService = Depends(get_subtema_service),
    current_user: dict = Depends(get_current_user)
):
    return await svc.get_all_subtemas()


@router.get("/{tema_id}", response_model=SubtemaOut)
async def read_subtema(
    tema_id: int,
    svc: SubtemaService = Depends(get_subtema_service),
    current_user: dict = Depends(get_current_user)
):
    try:
        return await svc.get_subtema_by_id(tema_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/", response_model=SubtemaOut, status_code=201)
async def create_subtema(
    subtema: SubtemaCreate,
    svc: SubtemaService = Depends(get_subtema_service),
    current_user: dict = Depends(get_current_user)
):
    return await svc.create_subtema(subtema.model_dump())


@router.put("/{tema_id}", response_model=SubtemaOut)
async def update_subtema(
    tema_id: int,
    subtema_data: SubtemaUpdate,
    svc: SubtemaService = Depends(get_subtema_service),
    current_user: dict = Depends(get_current_user)
):
    try:
        return await svc.update_subtema(
            tema_id, subtema_data.model_dump(exclude_unset=True)
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{tema_id}", status_code=204)
async def delete_subtema(
    tema_id: int,
    svc: SubtemaService = Depends(get_subtema_service),
    current_user: dict = Depends(get_current_user)
):
    try:
        await svc.delete_subtema(tema_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))