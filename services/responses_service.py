# services/responses_service.py
import asyncio
import json
from typing import AsyncIterator
from tenacity import retry, stop_after_attempt, wait_exponential_jitter, retry_if_exception_type
from openai import APIConnectionError, APIError, RateLimitError
from openai_client import client
from repositories.asistente_repository import AsistenteRepository
from services.pregunta_service import PreguntaService
from services.evaluacion_service import EvaluacionService
from config.db_config import AsyncSessionLocal

RETRYABLE = (APIConnectionError, APIError, RateLimitError)

class ChatServiceStream:
    def __init__(self, db, semaphore: asyncio.Semaphore) -> None:
        self.db = db
        self.semaphore = semaphore

    async def _registrar_y_clasificar(self, texto: str, asistente_id: str, estudiante_id: int):
        """
        Registra y clasifica la pregunta. Ahora crea y gestiona su PROPIA sesión de BD.
        """
        async with AsyncSessionLocal() as db_propia: 
            try:
                as_repo = AsistenteRepository(db=db_propia) 
                asistente_db = await as_repo.get_by_id(asistente_id=asistente_id)
                
                if not asistente_db:
                    print(f"ERROR: No se encuentra el asistente con ID {asistente_id} en _registrar_y_clasificar")
                    return

                pregunta_service = PreguntaService(db=db_propia) 
                resultado = await pregunta_service.insertar_y_clasificar_pregunta(
                    texto=texto,
                    vector_store_id=asistente_db.vs_temas_id,
                    estudiante_id=estudiante_id,
                    asistente_id=asistente_id,
                )

                await db_propia.commit() 
                print("INFO: Pregunta registrada y clasificada exitosamente en background.")
                return resultado

            except Exception as e:
                await db_propia.rollback() 
                print(f"ERROR: Falló _registrar_y_clasificar en background: {e}")

    async def _resolver_tool_calls(self, tool_calls, *, thread_id: str, estudiante_id: int, asistente_id: str) -> list[dict]:
        outputs = []
        ev_svc = EvaluacionService(self.db)
        for call in tool_calls:
            nombre = call.function.name
            args = json.loads(call.function.arguments)
            if nombre == "iniciar_evaluacion":
                salida = await ev_svc.iniciar_evaluacion(
                    data=args,
                    estudiante_id=estudiante_id,
                    asistente_id=asistente_id
                )
                outputs.append({"tool_call_id": call.id, "output": json.dumps(salida)})
            elif nombre == "calificar_evaluacion":
                evaluation_id = args.get("evaluation_id")
                salida = await ev_svc.calificar_evaluacion(
                    thread_id=thread_id,
                    evaluation_id=evaluation_id,
                )
                outputs.append({"tool_call_id": call.id, "output": json.dumps(salida)})
            else:
                outputs.append({"tool_call_id": call.id, "output": json.dumps({"error": f"Función {nombre} no soportada"})})
        return outputs

    @retry(
        retry=retry_if_exception_type(RETRYABLE),
        stop=stop_after_attempt(3),
        wait=wait_exponential_jitter(max=30),
    )
    async def enviar_mensaje_stream(
        self,
        *,
        thread_id: str,
        texto: str,
        asistente_id: str,
        estudiante_id: int,
        truncation_last_messages: int = 8,
    ) -> AsyncIterator[str]:
        print("Entrando a enviar_mensaje_stream")
        async with self.semaphore:
            await client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=texto
            )
            print("Mensaje creado")
            reg_task = asyncio.create_task(
                self._registrar_y_clasificar(texto=texto, asistente_id=asistente_id, estudiante_id=estudiante_id)
            )

            async with client.beta.threads.runs.stream(
                thread_id=thread_id,
                assistant_id=asistente_id,
                truncation_strategy={"type": "auto"},
                tool_choice={"type": "file_search"}
            ) as stream:
                async for event in stream:
                    event_type = getattr(event, "event", None)
                    print(event) 

                    if event_type == "thread.message.delta":
                        delta = event.data.delta
                        if delta and delta.content:
                            for content_part in delta.content:
                                if content_part.type == 'text' and content_part.text:
                                    text_chunk = content_part.text.value
                                    if text_chunk:
                                        yield text_chunk

                    elif event_type == "thread.run.requires_action":
                        tool_calls = event.data.required_action.submit_tool_outputs.tool_calls
                        tool_outputs = await self._resolver_tool_calls(
                            tool_calls,
                            thread_id=thread_id,
                            estudiante_id=estudiante_id,
                            asistente_id=asistente_id,
                        )
                        await stream.submit_tool_outputs(tool_outputs)

                    elif event_type == "thread.run.failed": # O el evento de error específico
                        error_data = getattr(event.data, "last_error", None)
                        error_message = getattr(error_data, "message", "stream error")
                        print(f"ERROR en stream: {error_message}")
                        raise RuntimeError(error_message)

                    elif event_type == "thread.run.completed":
                        print("Run completado.")
                        break

                    else:
                        print(f"Evento recibido: {event_type}")


                # Espera a que el stream realmente termine si es necesario
                # final_run = await stream.get_final_run()
                # print("Estado final del run:", final_run.status)

                try:
                    await reg_task
                except Exception as e:
                    print(e)