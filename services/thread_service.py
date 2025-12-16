import asyncio
import base64
import binascii
import logging
import json
from typing import Dict, Any, List
from openai import APIConnectionError, APITimeoutError, RateLimitError, InternalServerError
from openai_client import client
from sqlalchemy.ext.asyncio import AsyncSession
from tenacity import retry, stop_after_attempt, wait_exponential_jitter, retry_if_exception_type, before_sleep_log
from models.thread import Thread
from repositories.asistente_repository import AsistenteRepository
from repositories.thread_repository import ThreadRepository
from schemas.mensaje_schema import MensajeOut
from services.evaluacion_service import EvaluacionService
from services.pregunta_service import PreguntaService
from fastapi import HTTPException

RETRYABLE = (APIConnectionError, APITimeoutError,
             RateLimitError, InternalServerError)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class ThreadService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.thread_repo = ThreadRepository(db)
        self.asistente_repo = AsistenteRepository(db)
        self.semaphore = asyncio.Semaphore(6)

    # ----- CRUD -----

    async def get_thread_by_id(self, id: str) -> Thread:
        thread = await self.thread_repo.get_by_id(id)
        if not thread:
            raise ValueError(f"Thread con id {id} no encontrado")
        return thread

    async def get_thread_by_alumno(self, estudiante_id: int) -> Thread:
        thread = await self.thread_repo.get_by_alumno(estudiante_id=estudiante_id)
        if not thread:
            thread_data = {"alumnoId": estudiante_id}
            return await self.create_thread(thread_data)
        return thread

    async def get_all_threads(self) -> List[Thread]:
        return await self.thread_repo.get_all()

    async def create_thread(self, thread_data: dict) -> Thread:
        thread_api = await client.beta.threads.create()

        thread_db = await self.thread_repo.create({
            "id": thread_api.id,
            "estudiante_id": thread_data["alumnoId"],
        }, asistente_id=thread_data["asistente_id"])
        return thread_db

    async def update_thread(self, id: str, update_data: Dict[str, Any]) -> Thread:
        thread = await self.thread_repo.get_by_id(id)
        if not thread:
            raise ValueError(
                f"No se puede actualizar, thread con id {id} no encontrado")
        return await self.thread_repo.update(thread, update_data)

    async def delete_thread(self, id: str) -> None:
        thread = await self.thread_repo.get_by_id(id)
        if not thread:
            raise ValueError(
                f"No se puede eliminar, thread con id {id} no encontrado")
        await self.thread_repo.delete(thread)

    # ----- HELPERS -----

    def _to_base64(self, data: bytes | str) -> str:
        if isinstance(data, bytes):
            return base64.b64encode(data).decode()
        try:
            base64.b64decode(data, validate=True)
            return data.strip()
        except binascii.Error:
            return base64.b64encode(data.encode("latin1")).decode()

    # ----- FUNCIONES PRINCIPALES -----

    @retry(
        retry=retry_if_exception_type(RETRYABLE),
        stop=stop_after_attempt(3),
        wait=wait_exponential_jitter(max=30),
    )
    async def enviar_mensaje(self, id: str, texto: str, asistente_id: str, estudiante_id: int):
        """
        Orquesta el flujo de interacción con el asistente:

        1. Crea un mensaje con `client.beta.threads.message.create`.
        2. Llama a `VectorService.insertar_y_clasificar_pregunta` para clasificar la pregunta y
        grabarla en la DB.
        3. Inicia la ejecución de un run con `client.beta.threads.runs.create` con los parámetros
        necesarios y le pasa las instrucciones específicas de cada asistente como instrucciones
        adicionales.
        4. Hace polling hasta obtener un status diferente a `queued` o `in_progress`.
        5. Si run.status es `requires_action` llama a `procesar_tool_calls`.
        6. Una vez resuelto, retorna la run.
        """

        async with self.semaphore:

            as_repo = AsistenteRepository(db=self.db)

            msg_task = asyncio.create_task(
                client.beta.threads.messages.create(
                    thread_id=id, role='user', content=texto)
            )

            asistente_task = asyncio.create_task(
                as_repo.get_by_id(asistente_id=asistente_id))

            async def registrar_y_clasificar():
                asistente_db = await asistente_task
                if not asistente_db:
                    raise ValueError(
                        f"No se encuentra el asistente con ID {asistente_id}")
                pregunta_service = PreguntaService(db=self.db)
                return await pregunta_service.insertar_y_clasificar_pregunta(
                    texto=texto,
                    vector_store_id=asistente_db.vs_temas_id,
                    estudiante_id=estudiante_id,
                    asistente_id=asistente_id
                )

            registro_task = asyncio.create_task(registrar_y_clasificar())

            run = None

            try:

                await msg_task
                await asistente_task

                run = await client.beta.threads.runs.create(
                    thread_id=id,
                    assistant_id=asistente_id,
                    truncation_strategy={
                        "type": "last_messages",
                        "last_messages": 8
                    },
                    tool_choice={"type": "file_search"}
                )

                delay = 0.2
                while True:  # Use an indefinite loop
                    await asyncio.sleep(0.5)  # Consistent polling interval
                    run = await client.beta.threads.runs.retrieve(
                        thread_id=id,
                        run_id=run.id
                    )

                    # Success Condition
                    if run.status == "completed":
                        print("Run completed successfully.")
                        break

                    if run.status == "requires_action":
                        print("Run requires action.")
                        run = await self.procesar_tool_calls(
                            run=run,
                            thread_id=id,
                            estudiante_id=estudiante_id,
                            asistente_id=asistente_id
                            )
                    
                    if run.status in ["failed", "cancelled", "expired"]:
                        print(f"Run terminated with status: {run.status}")
                        error_message = "An unexpected error occurred."
                        if run.last_error:
                            error_message = run.last_error.message
                            print(f"OpenAI Error: {error_message}")
                        
                        raise HTTPException(
                            status_code=500,
                            detail=f"Assistant error: The request could not be completed. Details: {error_message}"
                        )
                    
                    print(f"Run still in progress with status: {run.status}")

                return run

            except Exception as e:
                if not (run and run.status in ("completed", "requires_action")):
                    registro_task.cancel()
                raise e

    @retry(
    retry=retry_if_exception_type(RETRYABLE),
    stop=stop_after_attempt(3),
    wait=wait_exponential_jitter(max=30),
    )
    async def enviar_mensaje_y_crear_run(self, id: str, texto: str, asistente_id: str, estudiante_id: int) -> str:
        """
        Paso 1 del flujo asincrónico: Orquesta las tareas iniciales, crea el mensaje, 
        inicia el run y devuelve su ID inmediatamente para la respuesta del endpoint.
        """

        print("DATA QUE ESTÁ LLEGANDO:")
        print(id)
        print(texto)
        print(asistente_id)
        print(estudiante_id)

        async with self.semaphore:
            # --- Lógica de inicialización movida aquí ---
            as_repo = AsistenteRepository(db=self.db)

            # Creamos las tareas en paralelo como hacías antes
            msg_task = asyncio.create_task(
                client.beta.threads.messages.create(thread_id=id, role='user', content=texto)
            )
            asistente_task = asyncio.create_task(
                as_repo.get_by_id(asistente_id=asistente_id)
            )

            async def registrar_y_clasificar():
                asistente_db = await asistente_task
                if not asistente_db:
                    raise ValueError(f"No se encuentra el asistente con ID {asistente_id}")
                pregunta_service = PreguntaService(db=self.db)
                return await pregunta_service.insertar_y_clasificar_pregunta(
                    texto=texto,
                    vector_store_id=asistente_db.vs_temas_id,
                    estudiante_id=estudiante_id,
                    asistente_id=asistente_id
                )

            registro_task = asyncio.create_task(registrar_y_clasificar())

            run = None
            try:
                # Esperamos a que las tareas críticas para iniciar el run terminen
                await msg_task
                await asistente_task

                # Ahora creamos el run
                run = await client.beta.threads.runs.create(
                    thread_id=id,
                    assistant_id=asistente_id,
                    truncation_strategy={
                        "type": "auto"
                    },
                    tool_choice={"type": "file_search"}
                )

                # Esperamos a que la tarea de registro también termine antes de devolver la respuesta.
                # Esto asegura que la pregunta se guarda antes de que el frontend pueda hacer algo más.
                await registro_task

                return run.id

            except Exception as e:
                # Si algo falla aquí (ej: crear el run), cancelamos la tarea de registro
                # para no dejar datos inconsistentes.
                if not (run and run.status in ("completed", "requires_action")):
                    registro_task.cancel()
                
                # Relanzamos la excepción para que el endpoint la maneje
                raise e
            
    @retry(
    retry=retry_if_exception_type(RETRYABLE),
    stop=stop_after_attempt(3),
    wait=wait_exponential_jitter(max=30),
    )
    async def _retrieve_run_with_retry(self, thread_id: str, run_id: str):
        """
        Obtiene el estado de un run de forma segura, con reintentos.
        """
        return await client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)

    retry(
        retry=retry_if_exception_type(RETRYABLE),
        stop=stop_after_attempt(3),
        wait=wait_exponential_jitter(max=30),
        before_sleep=lambda retry_state: logger.warning(
            f'Reintentando función: {retry_state.fn.__name__},'
            f'intento {retry_state.attempt_number} debido a: {retry_state.outcome.exception()}'
        )
    )
    async def procesar_tool_calls(self, run, thread_id: str, estudiante_id: int, asistente_id: str):
        """
        Gestiona las llamadas a funciones externas desde la API de OpenAI. Si detecta el estado
        `requires_action` procede a llamar a la función indicada en `call.function.name`.
        """
        async with self.semaphore:
            while run.status == "requires_action":
                outputs = []
                ev_svc = EvaluacionService(self.db)

                for call in run.required_action.submit_tool_outputs.tool_calls:
                    nombre = call.function.name
                    args = json.loads(call.function.arguments)

                    if nombre == "iniciar_evaluacion":
                        print("--- ENTRAMOS A INICIAR EVALUACIÓN ---")
                        salida = await ev_svc.iniciar_evaluacion(
                            data=args,
                            estudiante_id=estudiante_id,
                            asistente_id=asistente_id
                        )
                        print("--- SALIDA DE INICIAR_EVALUACION AL ASISTENTE: ---")
                        print(salida)
                        outputs.append(
                            {"tool_call_id": call.id, "output": json.dumps(salida)})
                    elif nombre == "calificar_evaluacion":
                        print("--- ENTRAMOS A CALIFICAR EVALUACIÓN ---")
                        evaluation_id = args.get("evaluation_id")
                        print(f"EVALUACION ID: {evaluation_id}")
                        salida = await ev_svc.calificar_evaluacion(
                            thread_id=thread_id,
                            evaluation_id=evaluation_id,
                        )
                        print("--- SALIDA DE CALIFICAR_EVALUACION AL ASISTENTE ---")
                        outputs.append(
                            {"tool_call_id": call.id, "output": json.dumps(salida)})
                    else:
                        outputs.append({"tool_call_id": call.id, "output": json.dumps(
                            {"error": f"Función {nombre} no soportada"}
                        )})

                run = await client.beta.threads.runs.submit_tool_outputs_and_poll(
                    thread_id=thread_id, run_id=run.id, tool_outputs=outputs
                )
            return run

    async def get_mensajes(self, thread_id: str) -> list[MensajeOut]:
        """
        Obtiene los mensajes desde la API de OpenAI y los mapea a una lista,
        chequeando si contiene mensajes o si se trata solo de texto.
        Incluye una verificación para ignorar archivos corruptos, que pueden
        aparecer si falla el llamado interno al intérprete de código del LLM.
        """
        resp = await client.beta.threads.messages.list(thread_id=thread_id, limit=30)
        mensajes: list[MensajeOut] = []

        for m in resp.data:
            partes = []
            for c in m.content:
                if c.type == "text":
                    partes.append({"type": "text", "text": c.text.value})
                
                elif c.type == "image_file":
                    if c.image_file.file_id:
                        try:
                            raw = await client.files.content(c.image_file.file_id)
                            b64 = self._to_base64(raw.content)
                            partes.append(
                                {"type": "image", "data_url": f"data:image/png;base64,{b64}"}
                            )
                        except Exception as e:
                            print(f"ERROR: No se pudo procesar el file_id {c.image_file.file_id}. Error: {e}")
                            partes.append({"type": "text", "text": "[Error: No se pudo cargar una imagen]"})
                    else:
                        print(f"WARN: Se encontró una referencia de archivo corrupta (file_id vacío) en el mensaje {m.id}. Se ignorará.")

            mensajes.append(MensajeOut(id=m.id, rol=m.role,
                                        partes=partes, fecha=m.created_at))
            
        return sorted(mensajes, key=lambda x: x.fecha)
    
    async def procesar_run_en_background(self, id: str, run_id: str, asistente_id: str, estudiante_id: int):
        """
        Esta función se ejecuta en segundo plano. Contiene el bucle de polling
        y orquesta el proceso hasta que el run llega a un estado terminal.
        """
        while True:
            try:
                run = await self._retrieve_run_with_retry(thread_id=id, run_id=run_id)

                if run.status == "completed":
                    print("BACKGROUND: Run completed successfully.")
                    break

                if run.status == "requires_action":
                    print("BACKGROUND: Run requires action.")
                    run = await self.procesar_tool_calls(
                        run=run,
                        thread_id=id,
                        estudiante_id=estudiante_id,
                        asistente_id=asistente_id
                    )

                if run.status in ["failed", "cancelled", "expired"]:
                    print(f"BACKGROUND: Run terminated with status: {run.status}")
                    error_message = "An unexpected error occurred."
                    if run.last_error:
                        error_message = run.last_error.message
                        print(f"BACKGROUND: OpenAI Error: {error_message}")
                    # Aquí podrías registrar el fallo en tu base de datos si lo necesitas.
                    break
                
                # Si el estado sigue siendo 'queued' o 'in_progress', simplemente esperamos.
                await asyncio.sleep(0.5)

            except Exception as e:
                # Si los reintentos de _retrieve_run_with_retry fallan, el error final se atrapa aquí.
                print(f"BACKGROUND: Error irrecuperable en el polling del run {run_id}: {e}")
                break

    async def cancelar_runs_pendientes(self, thread_id: str):
        runs_resp = await client.beta.threads.runs.list(thread_id=thread_id, limit=1)
        if not runs_resp.data:
            return
        run = runs_resp.data[0]
        if run.status in ("queued", "in_progress", "requires_action"):
            await client.beta.threads.runs.cancel(thread_id=thread_id, run_id=run.id)
