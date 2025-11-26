from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from schemas.thread_schema import ThreadOut
from services.thread_service import ThreadService
from schemas.mensaje_schema import MensajeOut
from config.db_config import get_db
from utils.dependencies import get_current_user

router = APIRouter(
    prefix="/threads",
    tags=["Threads"]
)

def get_thread_service(db: AsyncSession = Depends(get_db)) -> ThreadService:
    return ThreadService(db)

@router.get("/", response_model=List[ThreadOut])
async def read_threads(
    svc: ThreadService = Depends(get_thread_service),
    current_user: dict = Depends(get_current_user)
):
    return await svc.get_all_threads()


@router.get("/estudiante/{estudiante_id}", response_model=ThreadOut)
async def read_thread_by_alumno(
    estudiante_id: int,
    svc: ThreadService = Depends(get_thread_service),
    current_user: dict = Depends(get_current_user)
):
    try:
        return await svc.get_thread_by_alumno(estudiante_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{id}", response_model=ThreadOut)
async def read_thread(
    id: str,
    svc: ThreadService = Depends(get_thread_service),
    current_user: dict = Depends(get_current_user)
):
    try:
        return await svc.get_thread_by_id(id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/", response_model=ThreadOut, status_code=201)
async def create_thread(
    thread_data: dict,
    svc: ThreadService = Depends(get_thread_service),
    current_user: dict = Depends(get_current_user)
):
    # La llamada al servicio ahora usa await
    return await svc.create_thread(thread_data)


@router.delete("/{id}", status_code=204)
async def delete_thread(
    id: str,
    svc: ThreadService = Depends(get_thread_service),
    current_user: dict = Depends(get_current_user)
):
    try:
        await svc.delete_thread(id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{id}/messages", response_model=List[MensajeOut])
async def read_thread_messages(
    id: str,
    svc: ThreadService = Depends(get_thread_service)
):
    try:
        return await svc.get_mensajes(thread_id=id)
    except Exception as e:
        print(f"Error al obtener mensajes para el thread {id}: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener los mensajes.")

@router.post("/{id}")
async def enviar_mensaje_asincrono(
    id: str,
    mensaje_data: dict,
    background_tasks: BackgroundTasks,
    svc: ThreadService = Depends(get_thread_service)
):
    """
    Inicia la generación de la respuesta del asistente en segundo plano.
    NO espera a que se complete. Responde inmediatamente.
    """
    try:
        await svc.cancelar_runs_pendientes(thread_id=id)

        run_id = await svc.enviar_mensaje_y_crear_run(
            id=id,
            texto=mensaje_data["input"],
            asistente_id=mensaje_data["asistente_id"],
            estudiante_id=mensaje_data["estudiante_id"],
        )


        background_tasks.add_task(
            svc.procesar_run_en_background,
            id=id,
            run_id=run_id,
            asistente_id=mensaje_data["asistente_id"],
            estudiante_id=mensaje_data["estudiante_id"]
        )

        return JSONResponse(
            status_code=status.HTTP_202_ACCEPTED,
            content={"status": "processing_started", "run_id": run_id, "thread_id": id}
        )
    except Exception as e:
        print(f"Error inesperado al iniciar el run para el thread {id}: {e}")
        raise HTTPException(status_code=500, detail="No se pudo iniciar la solicitud.")


# --- NUEVO ENDPOINT PARA POLLING ---
@router.get("/{thread_id}/runs/{run_id}/status")
async def get_run_status(thread_id: str, run_id: str, svc: ThreadService = Depends(get_thread_service)):
    """
    Endpoint para que el frontend consulte el estado de un run.
    Es una llamada muy rápida y ligera, protegida con reintentos.
    """
    try:
        run = await svc._retrieve_run_with_retry(thread_id=thread_id, run_id=run_id)
        return {"status": run.status, "run_id": run.id}
    except Exception:
        raise HTTPException(status_code=404, detail="Run no encontrado.")
