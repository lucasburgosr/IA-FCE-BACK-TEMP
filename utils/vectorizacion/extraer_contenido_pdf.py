#Primero hay que ejecutar pip install --upgrade pymupdf4llm
import pymupdf4llm
import pathlib

# Le pasamos por parámetro la ruta del PDF
contenido = pymupdf4llm.to_markdown("A.3 - Continuidad.pdf")

# Esta línea convierte el documento a formato Markdown y lo guarda con el nombre especificado,
# en este caso "contenido_continuidad.md"
pathlib.Path("contenido_continuidad.md").write_bytes(contenido.encode())