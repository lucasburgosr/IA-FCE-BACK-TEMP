import json
import pathlib
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()
# Este bloque crea inserta preguntas de evaluaciones
VECTOR_STORE_ID = "vs_68c9c950cbc08191aaef45ced7414318"
JSONL_PATH = "./utils/embeddings/preguntas/preguntas_bloque_d_enriquecido.jsonl"

# Recupera tu vector store existente
vs = client.vector_stores.retrieve(vector_store_id=VECTOR_STORE_ID)

# Recorre cada línea del JSONL y sube el texto + metadata
with open(JSONL_PATH, encoding="utf-8") as f:
    for line in f:
        entry = json.loads(line)
        text = entry["text"]
        meta = entry["metadata"]

        # Genera un archivo .txt temporal para el texto
        qid = meta.get("question_id", "pregunta")
        txt_name = f"{qid}.txt"
        pathlib.Path(txt_name).write_text(text, encoding="utf-8")

        # Sube el archivo a OpenAI Files
        file = client.files.create(
            file=(txt_name, open(txt_name, "rb"), "text/plain"),
            purpose="assistants"
        )

        # Asocia el archivo al vector store, incluyendo toda la metadata
        client.vector_stores.files.create(
            vector_store_id=vs.id,
            file_id=file.id,
            attributes=meta
        )

print("✅ Todas las preguntas de evaluación han sido cargadas en el vector store.")

# Este bloque inserta temas de la materia en la vector store
""" VECTOR_STORE_ID = "vs_68c9c2c5a9748191b952550e1a4fbab6"
EMBEDDING_MODEL = "text-embedding-3-small"
JSONL_PATH = "./utils/embeddings/temas/bloque_d_matematicaii.jsonl"

vs = client.vector_stores.retrieve(
    vector_store_id=VECTOR_STORE_ID
)

for line in open(JSONL_PATH, encoding="utf8"):
    obj = json.loads(line)

    txt_name = f"{obj['metadata']['subtopic_id']}.txt"
    pathlib.Path(txt_name).write_text(obj["text"], encoding="utf8")

    file = client.files.create(
        file=(txt_name,
              open(txt_name, "rb"),
              "text/plain"),
        purpose="assistants"
    )

    client.vector_stores.files.create(
        vector_store_id=vs.id,
        file_id=file.id,
        attributes=obj["metadata"]
    ) """