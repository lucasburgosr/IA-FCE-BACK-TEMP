import os, json
from pathlib import Path

in_jsonl = "./jsonl/bloque_a_continuidad_chunks.jsonl"
out_dir = "./md/bloque_a_continuidad"
os.makedirs(out_dir, exist_ok=True)

def sanitize(s: str) -> str:
    return "".join(c if c.isalnum() or c in "-_." else "_" for c in s)[:80]

with open(in_jsonl, "r", encoding="utf-8") as f:
    for idx, line in enumerate(f, 1):
        rec = json.loads(line)
        meta = rec["metadata"]
        text = rec["text"].strip()

        # nombre de archivo estable y legible
        fname = f"{sanitize(meta['doc_id'])}__{meta['chunk_id'].replace('.', '_')}__{idx:04d}.txt"
        path = Path(out_dir) / fname

        header = [
            f"ID: {rec['id']}",
            f"DOC_ID: {meta['doc_id']}",
            f"CHUNK_ID: {meta['chunk_id']}",
            f"TITLE: {meta['title']}",
            f"LEVEL: {meta['level']}",
            f"PATH: {meta['path_str']}",
            f"SOURCE: {meta['source_path']}",
        ]

        with open(path, "w", encoding="utf-8") as o:
            # ⬇️ separador claro entre metadatos y contenido
            o.write("\n".join(header) + "\n---\n" + text + "\n")
print("Hecho →", out_dir)
