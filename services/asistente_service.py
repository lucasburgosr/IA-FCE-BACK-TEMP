import asyncio
from repositories.asistente_repository import AsistenteRepository
from models.asistente import Asistente
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from openai_client import client

class AsistenteService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.asistente_repo = AsistenteRepository(db)

    # Obtiene el asistente desde la API con su ID
    async def get_asistente_by_id(self, asistente_id: str) -> Asistente:
        # La llamada a la API es síncrona, se delega a un hilo secundario

        print("ASISTENTE ID")
        print(asistente_id)
        asistente = await client.beta.assistants.retrieve(
            assistant_id=asistente_id
        )
        if not asistente:
            raise ValueError(f"Asistente con el id {asistente_id} no encontrado")
        return asistente

    # Devuelve una lista de asistentes desde la base de datos
    async def get_all_asistentes(self) -> List[Asistente]:
        # Se espera la llamada asíncrona al repositorio
        return await self.asistente_repo.get_all()

    # Este método se encarga de actualizar tanto el objeto Asistente de la DB como el de la API.
    async def update_asistente(self, asistente_id: str, update_data: Dict[str, Any]) -> dict:
        # 1. Actualizar en OpenAI de forma no bloqueante
        asistente_api = await client.beta.assistants.update(
            assistant_id=asistente_id,
            instructions=update_data.get("instructions"),
            name=update_data.get("nombre")
        )

        # 2. Actualizar en base de datos de forma asíncrona
        asistente_db = await self.asistente_repo.get_by_id(asistente_id)
        if not asistente_db:
            raise ValueError(f"Asistente con id {asistente_id} no encontrado en la base de datos.")

        nueva_data = {}
        if "nombre" in update_data:
            nueva_data["nombre"] = update_data["nombre"]
        if "instructions" in update_data:
            nueva_data["instructions"] = update_data["instructions"]

        await self.asistente_repo.update(asistente_db, nueva_data)

        # 3. Devolver datos mapeados
        return {
            "asistente_id": asistente_api.id,
            "name": asistente_api.name,
            "instructions": asistente_api.instructions,
        }

    async def generar_prompt_draft(self, asistente_id: str, data: dict):
        # La implementación original ya era 'async' pero las llamadas eran bloqueantes.
        # Ahora se ejecutan en hilos separados.
        a = await client.beta.assistants.retrieve(
            assistant_id=asistente_id
        )
        prompt_base = a.instructions.strip()

        msg_system = {
            "role": "system",
            "content": (
                """Eres un generador de prompts de sistema para asistentes
                OpenAI de Matemática I. Tu tarea es modificar el prompt base
                según los parámetros proporcionados, sin cambiar lo referido a evaluaciones."""
            ),
        }

        msg_user = self.construir_prompt_usuario({**data, "base_prompt": prompt_base})

        rsp = await client.chat.completions.create(
            model="gpt-4o",
            messages=[msg_system, msg_user],
            temperature=0.3
        )

        return {"draft": rsp.choices[0].message.content.strip()}

    def construir_prompt_usuario(self, data: dict) -> dict:
        # Este método no realiza I/O, es solo procesamiento en memoria.
        # No necesita ser 'async'.
        base_prompt = data["base_prompt"].strip()
        instrucciones_extra = []
        instrucciones_extra.append(f"Adapta el prompt al NIVEL del estudiante: **{data['nivel']}**.")
        if data.get("lenguaje_tecnico"):
            instrucciones_extra.append("Reescribe las explicaciones usando lenguaje técnico de la materia")
        if data.get("ejemplos_economia"):
            instrucciones_extra.append("Incluye ejemplos relacionados con contextos económicos cuando sea apropiado.")

        contenido_usuario = (
            "PROMPT ORIGINAL:\n"
            f"```\n{base_prompt}\n```\n\n"
            "PARÁMETROS DE ADAPTACIÓN:\n"
            + "\n".join(f"- {inst}" for inst in instrucciones_extra) +
            "\n\nDevuelve el **prompt completo final** listo para usar."
        )

        return {"role": "user", "content": contenido_usuario}