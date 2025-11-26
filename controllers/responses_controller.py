# controller/chat_controller.py
from fastapi import APIRouter, Request, Depends
from fastapi.responses import StreamingResponse
from services.responses_service import ChatServiceStream
from config.db_config import get_db
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio
import async_timeout  # <--- 1. IMPORTAR LA BIBLIOTECA

router = APIRouter()

router = APIRouter(
    prefix="/responses",
    tags=["Responses"]
)

_sem = asyncio.Semaphore(6)

@router.get("/chat/stream")
async def chat_stream(request: Request, thread_id: str, texto: str, asistente_id: str, estudiante_id: int, db: AsyncSession = Depends(get_db), limiter = _sem):

    svc = ChatServiceStream(db=db, semaphore=limiter)

    async def gen():
        try:
            iterador_stream = svc.enviar_mensaje_stream(
                thread_id=thread_id,
                texto=texto,
                asistente_id=asistente_id,
                estudiante_id=estudiante_id,
            )
            async with async_timeout.timeout(180.0):
                async for delta in iterador_stream:
                    if await request.is_disconnected():
                        break
                    yield f"data: {delta}\n\n"
                
                yield "event: done\ndata: {}\n\n"
                
        except asyncio.TimeoutError:
            print(f"Error: Stream del thread {thread_id} superó los 180 segundos.")
            yield f"event: error\ndata: El asistente está tardando demasiado. Por favor, volvé a intentar en unos segundos."
        except Exception as e:
            yield f"event: error\ndata: {str(e)}\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream")