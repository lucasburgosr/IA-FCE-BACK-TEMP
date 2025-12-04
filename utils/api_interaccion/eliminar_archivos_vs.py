import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

response = client.vector_stores.files.list(
    vector_store_id="vs_6834c31e42e48191b3f5cad6596f7170", limit=100)

archivos = response.data

print("Cantidad de archivos en la vector store: ", len(archivos))

for a in archivos:
    print(a.attributes)

for a in archivos:
        client.vector_stores.files.delete(file_id=a.id, vector_store_id="vs_6834c31e42e48191b3f5cad6596f7170")
        print(f"Archivo con ID {a.id} eliminado de la vector store")
        client.files.delete(file_id=a.id)
        print(f"Archivo con ID {a.id} eliminado de la API")