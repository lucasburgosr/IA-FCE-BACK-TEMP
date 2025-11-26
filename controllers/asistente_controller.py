from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from schemas.asistente_schema import AsistenteDBOut, AsistenteUpdate, AsistenteOpenAIOut
from services.asistente_service import AsistenteService
from config.db_config import get_db
from utils.dependencies import get_current_user

router = APIRouter(
    prefix="/asistentes",
    tags=["Asistentes"]
)

# --- Inyección de dependencias para el servicio ---
def get_asistente_service(db: AsyncSession = Depends(get_db)) -> AsistenteService:
    return AsistenteService(db)


@router.get("/", response_model=List[AsistenteDBOut])
async def read_asistentes(svc: AsistenteService = Depends(get_asistente_service)):
    return await svc.get_all_asistentes()


@router.get("/{asistente_id}", response_model=AsistenteOpenAIOut)
async def read_asistente(
    asistente_id: str,
    svc: AsistenteService = Depends(get_asistente_service),
    current_user: dict = Depends(get_current_user)
):
    try:
        asistente_openai = await svc.get_asistente_by_id(asistente_id)
        # La validación con el schema de Pydantic sigue siendo una buena práctica
        asistente_dict = {
            "asistente_id": asistente_openai.id,
            "name": asistente_openai.name,
            "instructions": asistente_openai.instructions,
        }
        return AsistenteOpenAIOut.model_validate(asistente_dict)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{asistente_id}", response_model=AsistenteOpenAIOut)
async def update_asistente(
    asistente_id: str,
    asistente_data: AsistenteUpdate,
    svc: AsistenteService = Depends(get_asistente_service),
    current_user: dict = Depends(get_current_user)
):
    try:
        asistente_actualizado = await svc.update_asistente(
            asistente_id, asistente_data.model_dump(exclude_unset=True)
        )
        return AsistenteOpenAIOut.model_validate(asistente_actualizado)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{asistente_id}/generar_prompt")
async def generar_prompt(
    asistente_id: str,
    data: dict,
    svc: AsistenteService = Depends(get_asistente_service),
    current_user: dict = Depends(get_current_user)
):
    try:
        return await svc.generar_prompt_draft(asistente_id=asistente_id, data=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))