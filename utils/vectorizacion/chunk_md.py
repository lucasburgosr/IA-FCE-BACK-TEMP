from pathlib import Path

"""
chunk_md.py — Partir un documento Markdown en chunks por nivel de heading.

Jerarquía esperada (ejemplos):
# Matemática II
## BLOQUE A: FUNCIONES
### A.1/A.2/A.3
#### TEMA GLOBAL DEL DOCUMENTO
##### SUBTEMAS DENTRO DEL TEMA GLOBAL
###### SUBTEMAS DENTRO DEL SUBTEMA

Uso por CLI:
  python chunk_md.py input.md --level 5 --max-chars 1200 --out chunks.jsonl

Salida:
  JSON Lines con objetos:
    {
      "id": "1.2.1",
      "level": 5,
      "title": "SUBTEMAS DENTRO DEL TEMA GLOBAL",
      "path": ["Matemática II","BLOQUE A: FUNCIONES","A.1/A.2/A.3","TEMA GLOBAL DEL DOCUMENTO","SUBTEMAS DENTRO DEL TEMA GLOBAL"],
      "content": "..."
    }

También podés importarlo y usar split_markdown(text, chunk_level=5, max_chars=None).
"""

import argparse
import json
import re
from typing import List, Dict, Any, Tuple, Optional

HEADING_RE = re.compile(r'^(#{1,6})\s+(.*?)(?:\s+#+\s*)?$', re.M)

def _find_headings(text: str) -> List[Tuple[int, int, int, str]]:
    """
    Devuelve lista de (start_idx, end_idx, level, title) para cada heading.
    """
    headings = []
    for m in HEADING_RE.finditer(text):
        hashes, title = m.group(1), m.group(2).strip()
        level = len(hashes)
        headings.append((m.start(), m.end(), level, title))
    return headings

def _sections(text: str) -> List[Dict[str, Any]]:
    """
    Convierte headings en secciones con rangos: start_content/end_content.
    """
    hs = _find_headings(text)
    sections = []
    for i, (h_start, h_end, level, title) in enumerate(hs):
        # contenido comienza después del heading
        content_start = h_end
        # el contenido termina justo antes del próximo heading de nivel <= actual
        next_idx = len(text)
        for j in range(i + 1, len(hs)):
            if hs[j][2] <= level:
                next_idx = hs[j][0]
                break
        sections.append({
            "h_start": h_start,
            "h_end": h_end,
            "level": level,
            "title": title,
            "content_start": content_start,
            "content_end": next_idx,
        })
    return sections

def _build_paths(sections: List[Dict[str, Any]]) -> None:
    """
    Agrega el 'path' (lista de títulos desde nivel 1 hasta el actual)
    y un id ordinal por nivel (ej: "1.2.3").
    """
    stack: List[Tuple[int, str, int]] = []  # (level, title, ordinal)
    counters = [0] * 7  # índices 1..6

    for sec in sections:
        lvl = sec["level"]
        # reset counters for deeper levels
        for i in range(lvl + 1, 7):
            counters[i] = 0
        counters[lvl] += 1

        # mantener pila con títulos activos
        stack = [item for item in stack if item[0] < lvl]
        stack.append((lvl, sec["title"], counters[lvl]))

        sec["path"] = [t for _, t, _ in stack]
        sec["id"] = ".".join(str(n) for _, _, n in stack)

def _split_by_max_chars(content: str, max_chars: int) -> List[str]:
    """
    Parte por párrafos (doble salto) y si hace falta, por líneas,
    para no superar max_chars.
    """
    if len(content) <= max_chars:
        return [content]

    chunks: List[str] = []
    paragraphs = re.split(r'(\n\s*\n)', content)  # conserva separadores
    current = ""
    for part in paragraphs:
        if len(current) + len(part) <= max_chars:
            current += part
        else:
            if current.strip():
                chunks.append(current.strip())
            if len(part) <= max_chars:
                current = part
            else:
                # cortar por líneas si el párrafo es gigante
                lines = part.splitlines(keepends=True)
                buf = ""
                for ln in lines:
                    if len(buf) + len(ln) <= max_chars:
                        buf += ln
                    else:
                        if buf.strip():
                            chunks.append(buf.strip())
                        buf = ln
                current = buf
    if current.strip():
        chunks.append(current.strip())
    return chunks

def split_markdown(md_text: str, *, chunk_level: int = 5, max_chars: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Parte el Markdown y devuelve una lista de chunks (dicts).
    - chunk_level: nivel de heading que define “un chunk” (1..6).
    - max_chars: si se indica, re-parte cada chunk para no exceder ese largo.
    """
    if not (1 <= chunk_level <= 6):
        raise ValueError("chunk_level debe estar entre 1 y 6")

    secs = _sections(md_text)
    if not secs:
        # documento sin headings: devolver un único chunk
        base = {"id": "1", "level": 0, "title": "(root)", "path": [], "content": md_text.strip()}
        if max_chars and len(base["content"]) > max_chars:
            out = []
            for i, sub in enumerate(_split_by_max_chars(base["content"], max_chars), 1):
                out.append({**base, "id": f"1.{i}", "content": sub})
            return out
        return [base]

    _build_paths(secs)

    # recolectar secciones del nivel deseado
    chunks: List[Dict[str, Any]] = []
    for sec in secs:
        if sec["level"] != chunk_level:
            continue
        content = md_text[sec["content_start"]:sec["content_end"]].strip("\n")
        item = {
            "id": sec["id"],
            "level": sec["level"],
            "title": sec["title"],
            "path": sec["path"],
            "content": content.strip(),
        }
        if max_chars and len(item["content"]) > max_chars:
            parts = _split_by_max_chars(item["content"], max_chars)
            for idx, sub in enumerate(parts, 1):
                chunks.append({**item, "id": f"{item['id']}.{idx}", "content": sub})
        else:
            chunks.append(item)
    return chunks

import json
import os
from datetime import datetime

def chunks_to_records(
    chunks,
    *,
    source_path: str,
    doc_id: str = None,                # <- ahora opcional
    namespace: str = "matematica_ii",
):
    records = []
    src_base = Path(source_path).stem   # p.ej. 'bloque_a_generalidades'
    _doc_id = doc_id or src_base        # si no pasás doc_id, usa el nombre del .md

    for idx, ch in enumerate(chunks, 1):
        rec = {
            "id": f"{namespace}:{_doc_id}:{ch['id']}",
            "text": ch["content"],
            "metadata": {
                "source_path": source_path,
                "source_basename": src_base,                  # útil para naming
                "doc_id": _doc_id,
                "chunk_id": ch["id"],
                "level": ch["level"],
                "title": ch["title"],
                "path": ch["path"],
                "path_str": " > ".join(ch["path"]),
                "created_at": datetime.utcnow().isoformat() + "Z",
            },
        }
        records.append(rec)
    return records


def write_jsonl(records, out_path: str):
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return out_path


def main():
    ap = argparse.ArgumentParser(description="Partir Markdown en chunks por nivel de heading.")
    ap.add_argument("input", help="Ruta del archivo .md de entrada")
    ap.add_argument("--level", type=int, default=5, help="Nivel de heading que define un chunk (1..6). Default: 5")
    ap.add_argument("--max-chars", type=int, default=None, help="Máx. caracteres por chunk (opcional)")
    ap.add_argument("--out", default="-", help="Salida: '-' (stdout) o ruta .jsonl")
    args = ap.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        text = f.read()
        
    chunks = split_markdown(text, chunk_level=args.level, max_chars=args.max_chars)

    if args.out == "-":
        # stdout: deja el comportamiento original (chunks “crudos”)
        for c in chunks:
            print(json.dumps(c, ensure_ascii=False))
    else:
        # archivo: genera registros con source_path y doc_id auto-derivado
        records = chunks_to_records(chunks, source_path=args.input)  # doc_id se deriva del .md
        write_jsonl(records, args.out)


if __name__ == "__main__":
    main()
