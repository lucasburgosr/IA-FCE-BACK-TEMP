from openai import OpenAI
import os

client = OpenAI()

vs_id = os.getenv("VECTOR_STORE_EVALUACIONES_ID")

""" files = client.vector_stores.files.list(vector_store_id=vs_id)

for file in files:
    print(file.model_dump_json())
    print("\n") """

""" response = client.vector_stores.search(
    vector_store_id=vs_id,
    query="pregunta examen",
)

print(response.data)

for doc in response.data:
    print("Texto:", doc.content.text)
    print("Metadata:", doc.metadata) """

client.beta.threads.runs.cancel(run_id="run_msDloyyoIZXa8FfvasFNIxR", thread_id="thread_gdweVUztJnlRCbDj3gNGMTcv")

