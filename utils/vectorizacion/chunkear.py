# Importamos las funciones del archivo chunk.md
from chunk_md import split_markdown, chunks_to_records, write_jsonl

# Le indicamos la ruta del archivo Markdown ya revisado
src_path = './bibliografia/matematica_ii/bloque_a_continuidad.md'

with open(src_path, encoding='utf-8') as f:
    md = f.read()

# Parte el Markdown en chunks
chunks = split_markdown(md, chunk_level=5, max_chars=1200)

# Estructura los chunks en un archivo JSONL para asignarle los metadatos correctamente  
records = chunks_to_records(chunks, source_path=src_path)

# Guardar el archivo. Le indicamos la ruta y el nombre, en este caso "./jsonl/bloque_a_continuidad_chunks.jsonl"
out_file = write_jsonl(records, "./jsonl/bloque_a_continuidad_chunks.jsonl")
print("JSONL listo:", out_file, f"({len(records)} registros)")