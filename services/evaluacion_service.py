from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, Any, List
from models.asistente import Asistente
from models.evaluacion import Evaluacion
from repositories.asistente_repository import AsistenteRepository
from repositories.evaluacion_repository import EvaluacionRepository
from services.vector_store_service import VectorService
import asyncio
import re
import json
from openai_client import client


class EvaluacionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.evaluacion_repo = EvaluacionRepository(db)
        self.asistente_repo = AsistenteRepository(db)

    async def get_evaluacion_by_id(self, evaluacion_id: int) -> Evaluacion:
        evaluacion = await self.evaluacion_repo.get_by_id(evaluacion_id)
        if not evaluacion:
            raise ValueError(
                f"Evaluación con id {evaluacion_id} no encontrada")
        return evaluacion

    async def get_all_evaluaciones(self) -> List[Evaluacion]:
        return await self.evaluacion_repo.get_all()

    async def get_evaluaciones_by_alumno(self, estudiante_id: int) -> List[Evaluacion]:
        return await self.evaluacion_repo.get_by_alumno(estudiante_id=estudiante_id)

    async def get_evaluaciones_by_asistente(self, asistente_id: str) -> List[Evaluacion]:
        return await self.evaluacion_repo.get_by_asistente(asistente_id=asistente_id)

    async def create_evaluacion(self, evaluacion_data: Dict[str, Any]) -> Evaluacion:
        return await self.evaluacion_repo.create(evaluacion_data)

    async def update_evaluacion(self, evaluacion_id: int, update_data: Dict[str, Any]) -> Evaluacion:
        evaluacion = await self.evaluacion_repo.get_by_id(evaluacion_id)
        if not evaluacion:
            raise ValueError(
                f"No se puede actualizar, evaluación con id {evaluacion_id} no encontrada")
        return await self.evaluacion_repo.update(evaluacion, update_data)

    async def delete_evaluacion(self, evaluacion_id: int) -> None:
        evaluacion = await self.evaluacion_repo.get_by_id(evaluacion_id)
        if not evaluacion:
            raise ValueError(
                f"No se puede eliminar, evaluación con id {evaluacion_id} no encontrada")
        await self.evaluacion_repo.delete(evaluacion)

    async def iniciar_evaluacion(self, data: dict, estudiante_id: int, asistente_id: str) -> Dict:

        """
        Inicia una evaluación para un estudiante.

        1. Se obtiene el tema de la evaluación y el número de preguntas deseado.
        2. Si no se especifica el tema, se retorna un error.
        3. Se valida que el asistente exista en la base de datos; si no, se lanza una excepción.
        4. Se clasifica el tema con `VectorService.clasificar_consulta` y se obtienen las preguntas
        relacionadas con `VectorService.obtener_preguntas`.
        5. Si ocurre un error al obtener las preguntas, se retorna el error.
        6. Se crea una nueva evaluación en la base de datos con la información obtenida.
        7. Finalmente, se devuelve el ID de la evaluación junto con las preguntas.

        Si todo es exitoso, la evaluación se marca como pendiente.
        """

        subtema_nombre = data.get("subtema")
        num_q = data.get("num_questions", 5)

        if not subtema_nombre:
            return {"error": "No se especificó un tema para la evaluación."}

        asistente_result = await self.db.execute(select(Asistente).where(Asistente.asistente_id == asistente_id))
        asistente_db = asistente_result.scalars().first()
        if not asistente_db:
            raise ValueError(f"Asistente con id {asistente_id} no encontrado.")
        vs_id = asistente_db.vs_evaluaciones_id

        vector_service = VectorService(self.db)

        subtema_id, tema_id, unidad_id = await vector_service.clasificar_consulta(subtema_nombre, vs_id, estudiante_id)

        preguntas = await vector_service.obtener_preguntas(subtema=subtema_nombre, subtema_id=subtema_id, n=num_q, vector_store_id=vs_id)

        if isinstance(preguntas, dict) and "error" in preguntas:
            return preguntas

        evaluacion_data = {
            "nota": 0,
            "subtema_id": subtema_id,
            "estudiante_id": estudiante_id,
            "asistente_id": asistente_id,
            "pendiente": True
        }

        evaluacion_db = await self.create_evaluacion(evaluacion_data)

        print(preguntas)

        return {
            "evaluation_id": evaluacion_db.evaluacion_id,
            "questions": preguntas
        }
    

    def extraer_texto_de_mensaje(self, msg) -> str:
        partes = []
        for b in getattr(msg, "content", []) or []:
            t = getattr(b, "type", None)
            if t == "text":
                # En SDK v1, el texto está en .text.value
                partes.append(b.text.value)
            elif t == "input_text":
                # Algunos bloques pueden venir como input_text
                partes.append(getattr(b, "input_text", ""))
            elif t == "tool_result":
                # tool_result puede contener sub-bloques de texto en .content
                for c in getattr(b, "content", []) or []:
                    if getattr(c, "type", None) == "text":
                        partes.append(c.text.value)
            # Ignora bloques no textuales: image_file, image_url, file_path, etc.
        return " ".join(p for p in partes if p)

    async def calificar_evaluacion(self, thread_id: str, evaluation_id: int) -> dict:
        """
        Esta función tiene como objetivo calificar una evaluación basada en el historial de una conversación.

        1. Se obtiene el historial de mensajes de una conversación, limitando el número de mensajes a 5.
        2. Se construye un prompt que se utiliza para hacer una llamada stateless a la API de Chat Completions,
        en donde se le pide al modelo que analice las preguntas y respuestas del historial de la conversación y
        proporcione una calificación (nota final) del 0 al 10 junto con un comentario general sobre el desempeño del estudiante.
        3. Se realiza una llamada a la API de Chat Completions para obtener la calificación y el comentario basado en el
        historial de la conversación.
        4. Si la llamada a la API es exitosa, la calificación obtenida se utiliza para actualizar el estado de la evaluación
        en la base de datos, marcándola como "no pendiente".
        5. Finalmente, la función devuelve el estado de la evaluación junto con la calificación final.

        En caso de error en la llamada a la API, se captura la excepción y se retorna un mensaje de error.
        """
        try:
            messages_response = await client.beta.threads.messages.list(
                thread_id=thread_id,
                limit=10
            )
            # Construye el historial solo con bloques de texto
            lines = []
            for msg in reversed(messages_response.data):
                texto = self.extraer_texto_de_mensaje(msg)
                if texto:
                    lines.append(f"{msg.role}: {texto}")
            conversation_history = "\n".join(lines)

            prompt_calificacion = f"""
            Eres un experto evaluador de materias universitarias. A continuación te proporciono el historial de una conversación.
            Tu tarea es identificar las preguntas de la evaluación y las respuestas proporcionadas por el 'user'.
            Basado en esto, proporciona una nota final del 0 al 10.

            Historial de la Conversación:
            ---
            {conversation_history}
            ---

            Basado en el historial, devuelve EXCLUSIVAMENTE un objeto JSON con la siguiente estructura:
            {{
            "nota_final": <un número entero o flotante del 0 al 10>,
            "feedback_general": "Un breve comentario sobre el desempeño del estudiante."
            }}
            """.strip()

            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": prompt_calificacion}],
                response_format={"type": "json_object"},
                temperature=0.0
            )
            contenido = response.choices[0].message.content
            # content será un string JSON (con response_format=json_object)
            resultado_json = json.loads(contenido)
            nota_final = resultado_json.get("nota_final", 0)

            ev_svc = EvaluacionService(db=self.db)
            await ev_svc.update_evaluacion(evaluation_id, {"nota": nota_final, "pendiente": False})

            return {"status": "calificado", "nota": nota_final}

        except Exception as e:
            # Log detallado y retorno controlado
            return {"error": f"Hubo un problema al procesar la calificación: {type(e).__name__}: {e}"}
