import asyncio
import re
from typing import List, Dict, Optional, Set

from openai import OpenAI
from openai_client import client
from sqlalchemy.ext.asyncio import AsyncSession

sync_client = OpenAI()

SCORE_MIN = 0.35
SCORE_GAP = 0.01
MAX_RESULTS = 3

GENERIC_FOLLOWUP_TOKENS = {
    "seguimos", "continuemos", "continuá", "continuar", "otro", "otra", 
    "ok", "dale", "si", "sí"
}

ACTION_VERBS: Set[str] = {
    "dame", "tomame", "haceme", "mostrame",
}
ACTION_NOUNS: Set[str] = {
    "ejercicio", "ejercicios", "practica", "práctica", 
    "examen", "ejemplo", "ejemplos", "prueba", "test"
}

FOLLOWUP_REGEX = [
    re.compile(r"^\s*(otro|otra|seguimos|continuemos|continuá|continuar)\b", re.IGNORECASE),
    re.compile(r"^\s*(ok|dale|sí|si)\s*$", re.IGNORECASE),
]

class VectorService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.SCORE_MIN = SCORE_MIN
        self.SCORE_GAP = SCORE_GAP
        self.MAX_RESULTS = MAX_RESULTS
        self.GENERIC_FOLLOWUP_TOKENS = GENERIC_FOLLOWUP_TOKENS
        self.ACTION_VERBS = ACTION_VERBS
        self.ACTION_NOUNS = ACTION_NOUNS
        self.FOLLOWUP_REGEX = FOLLOWUP_REGEX

    def tokenizar(self, texto: str) -> List[str]:
        return re.findall(r"[a-záéíóúüñ0-9]+", texto.lower())

    def es_followup_generico(self, texto: str) -> bool:
        """
        Detecta follow-ups simples y genéricos.
        """
        t_low = texto.lower().strip()
        
        if any(p.search(t_low) for p in self.FOLLOWUP_REGEX):
            return True
            
        tokens = set(self.tokenizar(t_low))
        return (0 < len(tokens) <= 3) and tokens.issubset(self.GENERIC_FOLLOWUP_TOKENS)

    def es_pregunta_de_accion(self, texto: str) -> bool:
        """
        Detecta si el texto es una solicitud de acción contextual.
        """
        tokens = set(self.tokenizar(texto))
        num_tokens = len(self.tokenizar(texto))

        # Verificamos si la frase contiene palabras de cada categoría
        contiene_verbo_accion = not tokens.isdisjoint(self.ACTION_VERBS)
        contiene_sustantivo_accion = not tokens.isdisjoint(self.ACTION_NOUNS)

        if contiene_verbo_accion and contiene_sustantivo_accion:
            return True

        if contiene_sustantivo_accion and num_tokens <= 3: # Este umbral es ajustable
            return True
        
        return False

    async def clasificar_consulta(self, texto: str, vector_store_id: str, estudiante_id: int) -> List[int]:
        from services.pregunta_service import PreguntaService

        async def get_last_ids() -> Optional[List[int]]:
            ps = PreguntaService(self.db)
            ultima = await ps.get_ultima_pregunta_by_estudiante(estudiante_id=estudiante_id)
            return None if ultima is None else [ultima.subtema_id, ultima.unidad_id]

        last_ids_task = asyncio.create_task(get_last_ids())

        # Esta función entrega los ID de tema y unidad de la última pregunta existente en la DB
        async def try_fallback_if_any(reason: str) -> Optional[List[int]]:
            ids = await last_ids_task
            if ids is not None:
                print(f"[clasificar_consulta] Fallback por {reason}.")
            return ids

        # FILTRO 1: Texto muy corto
        if len(self.tokenizar(texto)) <= 1:
            if (fb := await try_fallback_if_any("texto muy corto")) is not None:
                return fb

        # FILTRO 2: Follow-up genérico
        if self.es_followup_generico(texto):
            if (fb := await try_fallback_if_any("follow-up genérico")) is not None:
                return fb
        
        # FILTRO 3 (NUEVO): Pregunta de acción contextual
        if self.es_pregunta_de_accion(texto):
            if (fb := await try_fallback_if_any("pregunta de acción")) is not None:
                return fb
            # Si no hay contexto previo, una acción no tiene sentido.
            raise ValueError("Se solicitó una acción (ej. ejercicio) sin un tema de contexto previo.")
            
        # --- BÚSQUEDA VECTORIAL (Si pasa todos los filtros) ---
        vector_task = asyncio.create_task(asyncio.to_thread(
            sync_client.vector_stores.search,
            vector_store_id=vector_store_id, query=texto, max_num_results=self.MAX_RESULTS
        ))

        try:
            resp = await asyncio.wait_for(vector_task, timeout=5)
            hits = resp.data or []
        except Exception as e:
            print(f"[clasificar_consulta] Error/timeout en vector store: {e}")
            if (fb := await last_ids_task) is not None:
                return fb
            raise

        if not hits:
            print("[clasificar_consulta] Sin resultados del vector store.")
            if (fb := await last_ids_task) is not None:
                return fb
            raise ValueError("No hay resultados y no existe última pregunta para fallback.")

        best = hits[0]

        try:
            subtopic_int = int(float(best.attributes["subtopic_id"]))
            topic_int = int(float(best.attributes["topic_id"]))
            unit_int = int(float(best.attributes["unit_id"]))

            # --- FILTRO DE SEGURIDAD ---
            # Si los IDs son 0 o inválidos, lo consideramos un mal resultado.
            if subtopic_int == 0 or unit_int == 0 or topic_int == 0:
                print(f"[clasificar_consulta] IDs inválidos en los atributos.")
                if (fb := await last_ids_task) is not None:
                    return fb
                # Si no hay fallback, es un error porque los IDs son incorrectos.
                raise ValueError("Resultado con IDs inválidos y sin fallback.")
        except Exception as e:
            print(f"[clasificar_consulta] Atributos faltantes/mal tipeados ({e}).")
            if (fb := await last_ids_task) is not None:
                return fb
            raise

        return [subtopic_int, topic_int, unit_int]

    async def obtener_preguntas(self, subtema: str, subtema_id: int, n: int, vector_store_id: str) -> List[Dict]:
        filters = {"key": "subtopic_id", "type": "eq", "value": str(subtema_id)}

        rsp = await asyncio.to_thread(
            sync_client.vector_stores.search,
            vector_store_id=vector_store_id,
            query=f"{subtema}",
            max_num_results=n,
            filters=filters
        )
        docs = rsp.data
        preguntas = [{"id": d.attributes.get("question_id"), "text": d.content[0].text if d.content else ""} for d in docs]
        
        faltantes = n - len(preguntas)
        if faltantes > 0 or len(preguntas) == 0:
            ejemplos = [p["text"] for p in preguntas] if preguntas else []
            prompt = self._construir_prompt_generacion(subtema, subtema_id, faltantes, ejemplos)

            respuesta = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": "Sos un generador de preguntas de nivel universitario. "
                            "No incluyas respuestas ni explicaciones. "
                            "Separá cada pregunta con dos líneas en blanco."}, {"role": "user", "content": prompt}],
                temperature=0.7
            )
            raw_content = respuesta.choices[0].message.content
            texto = "\n".join(p["text"] for p in raw_content if "text" in p) if isinstance(raw_content, list) else raw_content
            nuevas_preguntas_textos = self._extraer_preguntas_generadas(texto)
            preguntas.extend([{"id": f"gen-{i}", "text": pregunta_generada} for i, pregunta_generada in enumerate(nuevas_preguntas_textos, start=1)])

        print("--- PREGUNTAS OBTENIDAS --- ")
        print(preguntas)
        
        return preguntas[:n]

    def _construir_prompt_generacion(self, subtema: str, subtema_id: int, cantidad: int, ejemplos: List[str]) -> str:
        prompt = (
            f"Genera {cantidad} preguntas tipo examen para el subtema \"{subtema}\" (ID {subtema_id}), "
            "relacionadas con el tema indicado. "
            "Las expresiones matemáticas (si las hay) deberán estar obligatoriamente "
            "escritas en formato LaTeX, usando el entorno:\n\n"
            "\\[\n\\begin{align*}\n...\n\\end{align*}\n\\]\n\n"
            "No incluyas respuestas ni explicaciones. No uses numeración. "
            "Separá cada pregunta con dos líneas en blanco.\n\n"
        )

        if ejemplos:
            prompt += "Aquí algunos ejemplos del estilo esperado:\n\n" + "\n\n".join(ejemplos)

        return prompt

    def _extraer_preguntas_generadas(self, texto: str) -> List[str]:
        preguntas = []
        buffer = ""
        dentro_de_pregunta = False

        for linea in texto.splitlines():
            linea = linea.strip()

            if not linea:
                continue

            if not dentro_de_pregunta and not linea.startswith("\\["):
                if buffer:
                    preguntas.append(buffer.strip())
                    buffer = ""
                buffer = linea
                dentro_de_pregunta = True

            elif linea.startswith("\\["):
                buffer += "\n" + linea
                dentro_de_pregunta = True

            elif linea.startswith("\\]"):
                buffer += "\n" + linea
                preguntas.append(buffer.strip())
                buffer = ""
                dentro_de_pregunta = False

            else:
                buffer += "\n" + linea

        if buffer:
            preguntas.append(buffer.strip())

        return preguntas