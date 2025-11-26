#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Extrae preguntas desde un HTML exportado de Moodle, preservando las fórmulas TeX
y las opciones de respuesta cuando existan.

Salida (JSONL): una línea por pregunta, con:
{
  "index": <int>,
  "id": "<str|None>",
  "name": "<str|None>",
  "title": "<str>",
  "statement": "<str>",        # enunciado con TeX
  "type": "<multiple_choice|match_drag_drop|single_choice|open_or_numeric>",
  "options": ["<str>", ...]    # si hay opciones; None si no hay
}
"""

import re
import json
import argparse
from pathlib import Path
from bs4 import BeautifulSoup, Comment
from tqdm import tqdm

COMMENT_Q_RE = re.compile(r"question:\s*(\d+)\s+name:\s*(.*)", re.IGNORECASE)

def find_leading_comment(div):
    """
    Busca un comentario inmediatamente anterior del tipo:
    <!-- question: <id>  name: <name> -->
    """
    node = div.previous_sibling
    while node and (str(node).strip() == "" or getattr(node, "name", None) in ["\n"]):
        node = node.previous_sibling
    if isinstance(node, Comment):
        m = COMMENT_Q_RE.search(str(node))
        if m:
            return m.group(1).strip(), m.group(2).strip()
    return None, None

def clean_spaces(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip())

def text_with_tex(tag) -> str:
    """
    Convierte el contenido HTML a texto preservando TeX:
    - Reemplaza <img class="texrender" ... alt="..."> por su alt (que trae el TeX).
    - Reemplaza <script type="math/tex">...</script> por su contenido TeX.
    """
    if tag is None:
        return ""
    # <img class="texrender" alt="...">
    for img in tag.find_all("img", class_="texrender"):
        alt = img.get("alt") or ""
        img.replace_with(alt)
    # <script type="math/tex">
    for sc in tag.find_all("script", attrs={"type": "math/tex"}):
        sc.replace_with(sc.get_text())
    # A texto plano
    txt = tag.get_text(" ", strip=True)
    txt = clean_spaces(txt)
    txt = re.sub(r"(\\frac\{[^}]+\}\{[^}]+\})\s*\1", r"\1", txt)  # ejemplo para fracciones duplicadas
    txt = re.sub(r"\s+", " ", txt).strip()
    return txt

def guess_type(qdiv):
    """
    Heurística del tipo de pregunta según estructura HTML de Moodle.
    """
    if qdiv.find("ul", class_="multichoice"):
        return "multiple_choice"
    if qdiv.find("ul", class_="match"):
        return "match_drag_drop"
    if qdiv.find("input", attrs={"type": "radio"}):
        return "single_choice"
    return "open_or_numeric"

def extract_multichoice(qdiv):
    """
    Extrae opciones de <ul class="multichoice">; toma el texto visible (con TeX).
    """
    out = []
    ul = qdiv.find("ul", class_="multichoice")
    if not ul:
        return out
    for li in ul.find_all("li", recursive=False):
        # la opción más limpia suele estar en un <p> dentro del <li>
        p = li.find("p")
        if p:
            out.append(text_with_tex(p))
        else:
            out.append(clean_spaces(li.get_text(" ", strip=True)))
    return out

def extract_match(qdiv):
    """
    Extrae estructura de preguntas tipo “relacionar/arrastrar” (<ul class="match">)
    Deja una lista de strings con el “lado izquierdo” y un dump JSON de opciones.
    (Si querés, podés modificar para separar mejor.)
    """
    ul = qdiv.find("ul", class_="match")
    if not ul:
        return []
    opts_union = set()
    rows = []
    for li in ul.find_all("li", recursive=False):
        left = text_with_tex(li.find("p") or li)
        sel = li.find("select")
        opts = []
        if sel:
            for opt in sel.find_all("option"):
                val = clean_spaces(opt.get_text())
                if val:
                    opts.append(val)
                    opts_union.add(val)
        # Guardamos como "izquierda -> opciones"
        rows.append(f"{left}  ==>  {', '.join(opts) if opts else '—'}")
    # Añadimos una línea final con el universo de opciones (útil para revisar)
    if opts_union:
        rows.append(f"[TODAS LAS OPCIONES]: {', '.join(sorted(opts_union))}")
    return rows

def extract_question(qdiv, idx):
    qid, qname = find_leading_comment(qdiv)

    # Título y enunciado con TeX
    h3 = qdiv.find("h3")
    title = text_with_tex(h3) if h3 else (qname or f"Pregunta {idx+1}")
    qtext = qdiv.find("p", class_="questiontext")
    statement = text_with_tex(qtext)

    qtype = guess_type(qdiv)

    # Opciones según tipo
    options = None
    if qtype == "multiple_choice" or qtype == "single_choice":
        options = extract_multichoice(qdiv)
    elif qtype == "match_drag_drop":
        options = extract_match(qdiv)

    return {
        "index": idx + 1,
        "id": qid or None,
        "name": qname or None,
        "title": title,
        "statement": statement or title,
        "type": qtype,
        "options": options if options else None,
    }

def main():
    ap = argparse.ArgumentParser(
        description="Extrae preguntas de un HTML de Moodle, preservando TeX y opciones."
    )
    ap.add_argument("input_html", help="Ruta al archivo .html")
    ap.add_argument("-o", "--output", default="preguntas_raw.jsonl", help="Salida JSONL")
    args = ap.parse_args()

    in_path = Path(args.input_html)
    if not in_path.exists():
        raise SystemExit(f"No existe el archivo: {in_path}")

    html = in_path.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(html, "lxml")

    qdivs = soup.find_all("div", class_="question")
    rows = []
    for i, qdiv in enumerate(tqdm(qdivs, desc="Extrayendo preguntas")):
        rows.append(extract_question(qdiv, i))

    # Emitir JSONL
    out_path = Path(args.output)
    with out_path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"✔ Extraídas {len(rows)} preguntas")
    print(f"   JSONL: {out_path}")

if __name__ == "__main__":
    main()