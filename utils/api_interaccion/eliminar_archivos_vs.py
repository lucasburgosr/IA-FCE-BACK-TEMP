import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

response = client.vector_stores.files.list(
    vector_store_id="vs_692e087391448191b1ab0ca35298e92f")

archivos = response.data

print("Cantidad de archivos en la vector store: ", len(archivos))

for a in archivos:
    print(a.attributes)

for a in archivos:
    if (a.id != 'file-E4dr4KynALZWxXy8xZkwP2' and a.id != 'file-XRbssPawsGdpZQPnQx4GpW' and a.id != 'file-NoyHqcfE78eieCxtv3EvkN'):
        client.vector_stores.files.delete(file_id=a.id, vector_store_id="vs_692e087391448191b1ab0ca35298e92f")
        print(f"Archivo con ID {a.id} eliminado de la vector store")
        client.files.delete(file_id=a.id)
        print(f"Archivo con ID {a.id} eliminado de la API")