from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from config.db_config import get_db
from utils.dependencies import get_current_user
from schemas.sesion_chat_schema import (
    SesionStartRequest,
    SesionStartResponse,
    SesionEndRequest
)
from services.sesion_chat_service import SesionService

router = APIRouter(prefix="/sesiones", tags=["Sesiones"])

# --- Inyección de dependencias para el servicio ---
def get_sesion_service(db: AsyncSession = Depends(get_db)) -> SesionService:
    return SesionService(db)


@router.post("/iniciar/{estudiante_id}", response_model=SesionStartResponse, status_code=status.HTTP_201_CREATED)
async def start_session(
    estudiante_id: int,
    req: SesionStartRequest,
    svc: SesionService = Depends(get_sesion_service),
    current_user: dict = Depends(get_current_user)
):
    session = await svc.start_session(estudiante_id, req.thread_id)
    return SesionStartResponse(sesion_id=session.sesion_id)


@router.post("/finalizar", status_code=status.HTTP_204_NO_CONTENT)
async def end_session(
    req: SesionEndRequest,
    svc: SesionService = Depends(get_sesion_service),
    current_user: dict = Depends(get_current_user)
):
    try:
        await svc.end_session(
            estudiante_id=req.estudiante_id,
            thread_id=req.thread_id,
            sesion_id=req.sesion_id
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))