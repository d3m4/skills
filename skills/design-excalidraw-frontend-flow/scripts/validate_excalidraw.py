"""Valida um .excalidraw: estrutura, vínculos e defeitos de layout.

Uso:
    python validate_excalidraw.py <arquivo.excalidraw> [--fix] [--strict]

ERROS (saída 1) quebram a edição à mão ou o arquivo:
  - estrutura do documento, id/type ausentes, ids duplicados;
  - seta sem startBinding/endBinding ou apontando para id inexistente;
  - vínculo de mão única: figura que não lista de volta a seta ou o texto,
    boundElements apontando para id inexistente ou para quem não aponta de volta.

AVISOS (saída 0, ou 1 com --strict) pedem olho no render:
  - texto que provavelmente não cabe no container;
  - figuras que se sobrepõem parcialmente;
  - seta atravessando uma figura que não é origem nem destino;
  - ponta de seta longe da figura à qual está ligada;
  - texto solto que parece rótulo de figura ou de seta (devia estar vinculado);
  - textos soltos sobrepostos;
  - protótipo textual: texto que escreve controles ("[ Salvar ]", "( ) opção",
    caixa ASCII) em vez de desenhá-los como figuras.

--fix corrige só o que é mecânico e seguro: acrescenta ao boundElements as
referências de volta que faltam e remove entradas que apontam para o nada.
Não cria vínculos novos nem mexe em coordenadas.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path

SHAPES = {"rectangle", "diamond", "ellipse"}
LINEAR = {"arrow", "line"}
PAD = 5  # BOUND_TEXT_PADDING do Excalidraw

# largura média por caractere / fontSize, medida no Excalidraw 0.18 (minúscula, maiúscula/dígito)
# sinais de controle de UI escrito como texto: [ Salvar ], ( ) opção, (•), [x], ┌──┐
TEXT_UI = [re.compile(p) for p in (r"\[ ?[^\]\n]{1,30}? ?\]", r"\(\s?[•x*o ]?\s?\)\s\w", r"[┌┐└┘│─]{2,}", r"_{6,}")]

CHAR_W = {5: (0.52, 0.64), 1: (0.53, 0.64), 2: (0.48, 0.60), 6: (0.48, 0.60), 3: (0.59, 0.59), 8: (0.55, 0.55)}


def text_size(el: dict) -> tuple[float, float]:
    low, up = CHAR_W.get(el.get("fontFamily", 5), (0.55, 0.65))
    fs = el.get("fontSize", 20)
    lines = (el.get("originalText") or el.get("text") or "").split("\n")
    w = max(sum((up if (c.isupper() or c.isdigit()) else low) for c in line) for line in lines) * fs
    return w, len(lines) * fs * el.get("lineHeight", 1.25)


def bbox(el: dict) -> tuple[float, float, float, float]:
    x, y = el.get("x", 0), el.get("y", 0)
    if el["type"] in LINEAR and el.get("points"):
        xs = [x + p[0] for p in el["points"]]
        ys = [y + p[1] for p in el["points"]]
        return min(xs), min(ys), max(xs), max(ys)
    if el["type"] == "text":
        # o width gravado no arquivo costuma ser chute de quem gerou o JSON; o que aparece
        # na tela é o texto medido, ancorado conforme o alinhamento
        w, h = text_size(el)
        sw = el.get("width", w)
        ax = {"left": x, "center": x + sw / 2 - w / 2, "right": x + sw - w}.get(el.get("textAlign", "left"), x)
        ay = y + (el.get("height", h) - h) / 2 if el.get("verticalAlign") == "middle" else y
        return ax, ay, ax + w, ay + h
    w, h = el.get("width", 0), el.get("height", 0)
    return min(x, x + w), min(y, y + h), max(x, x + w), max(y, y + h)


def inner_box(c: dict) -> tuple[float, float]:
    """Área útil para texto dentro do container, como o Excalidraw calcula."""
    w, h = abs(c.get("width", 0)), abs(c.get("height", 0))
    if c["type"] == "ellipse":
        return round(w / 2 * math.sqrt(2)) - 2 * PAD, round(h / 2 * math.sqrt(2)) - 2 * PAD
    if c["type"] == "diamond":
        return round(w / 2) - 2 * PAD, round(h / 2) - 2 * PAD
    return w - 2 * PAD, h - 2 * PAD


def overlap(a, b, m=0.0) -> bool:
    return a[0] < b[2] - m and b[0] < a[2] - m and a[1] < b[3] - m and b[1] < a[3] - m


def contains(outer, inner, m=0.0) -> bool:
    return outer[0] - m <= inner[0] and outer[1] - m <= inner[1] and inner[2] <= outer[2] + m and inner[3] <= outer[3] + m


def seg_hits_box(p, q, b) -> bool:
    """Liang–Barsky: o segmento p→q entra no retângulo b?"""
    (x0, y0), (x1, y1) = p, q
    dx, dy = x1 - x0, y1 - y0
    t0, t1 = 0.0, 1.0
    for pp, qq in ((-dx, x0 - b[0]), (dx, b[2] - x0), (-dy, y0 - b[1]), (dy, b[3] - y0)):
        if pp == 0:
            if qq < 0:
                return False
        else:
            r = qq / pp
            if pp < 0:
                t0 = max(t0, r)
            else:
                t1 = min(t1, r)
            if t0 > t1:
                return False
    return True


def dist_to_box(pt, b) -> float:
    dx = max(b[0] - pt[0], 0, pt[0] - b[2])
    dy = max(b[1] - pt[1], 0, pt[1] - b[3])
    if dx == 0 and dy == 0:  # dentro: distância até a borda mais próxima
        return min(pt[0] - b[0], b[2] - pt[0], pt[1] - b[1], b[3] - pt[1])
    return math.hypot(dx, dy)


def label(el: dict) -> str:
    t = (el.get("text") or "").replace("\n", " ")
    return f'{el["type"]} "{el["id"]}"' + (f' ("{t[:30]}")' if t else "")


def validate(doc: dict, fix: bool) -> tuple[list[str], list[str], int]:
    errors: list[str] = []
    warns: list[str] = []
    fixed = 0

    if doc.get("type") != "excalidraw":
        errors.append('documento sem "type": "excalidraw"')
    for key in ("version", "elements", "appState", "files"):
        if key not in doc:
            errors.append(f'documento sem "{key}"')
    if not isinstance(doc.get("elements"), list):
        return errors, warns, fixed

    seen: dict[str, dict] = {}
    for i, el in enumerate(doc["elements"]):
        if "id" not in el or "type" not in el:
            errors.append(f"elemento #{i} sem id ou type")
            continue
        if el["id"] in seen:
            errors.append(f'id duplicado "{el["id"]}"')
        seen[el["id"]] = el
    live = {k: v for k, v in seen.items() if not v.get("isDeleted")}

    def listed(owner: dict, child_id: str) -> bool:
        return any(b.get("id") == child_id for b in owner.get("boundElements") or [])

    def add_back(owner: dict, child: dict) -> None:
        nonlocal fixed
        owner["boundElements"] = (owner.get("boundElements") or []) + [{"type": child["type"], "id": child["id"]}]
        fixed += 1

    # setas: duas pontas ligadas e listadas de volta
    for el in live.values():
        if el["type"] != "arrow":
            continue
        for end in ("startBinding", "endBinding"):
            b = el.get(end)
            if not b or not b.get("elementId"):
                errors.append(f"{label(el)}: sem {end} (seta solta)")
                continue
            target = live.get(b["elementId"])
            if target is None:
                errors.append(f'{label(el)}: {end} aponta para "{b["elementId"]}", que não existe')
            elif not listed(target, el["id"]):
                if fix:
                    add_back(target, el)
                else:
                    errors.append(f"{label(target)} não lista a seta \"{el['id']}\" em boundElements")

    # texto vinculado: container existe e lista o texto
    for el in live.values():
        if el["type"] != "text" or not el.get("containerId"):
            continue
        c = live.get(el["containerId"])
        if c is None:
            errors.append(f'{label(el)}: containerId "{el["containerId"]}" não existe')
        elif not listed(c, el["id"]):
            if fix:
                add_back(c, el)
            else:
                errors.append(f"{label(c)} não lista o texto \"{el['id']}\" em boundElements")

    # boundElements: nada apontando para o vazio nem vínculo de mão única
    for el in live.values():
        keep = []
        for b in el.get("boundElements") or []:
            child = live.get(b.get("id"))
            if child is None:
                if fix:
                    fixed += 1
                    continue
                errors.append(f'{label(el)}: boundElements lista "{b.get("id")}", que não existe')
            elif child["type"] == "text" and child.get("containerId") != el["id"]:
                errors.append(f'{label(el)}: lista o texto "{child["id"]}", mas o texto não tem containerId para ela')
            elif child["type"] == "arrow" and el["id"] not in {
                (child.get("startBinding") or {}).get("elementId"),
                (child.get("endBinding") or {}).get("elementId"),
            }:
                errors.append(f'{label(el)}: lista a seta "{child["id"]}", mas a seta não está ligada a ela')
            keep.append(b)
        if fix and el.get("boundElements") is not None:
            el["boundElements"] = keep

    # ---------- avisos de layout ----------
    shapes = [e for e in live.values() if e["type"] in SHAPES]
    texts = [e for e in live.values() if e["type"] == "text"]
    arrows = [e for e in live.values() if e["type"] == "arrow"]
    boxes = {e["id"]: bbox(e) for e in live.values()}

    for t in texts:
        c = live.get(t.get("containerId") or "")
        if c is None or c["type"] not in SHAPES:
            continue
        tw, th = text_size(t)
        iw, ih = inner_box(c)
        if tw > iw + 2 or th > ih + 2:
            warns.append(f"texto não cabe em {label(c)}: precisa ~{tw:.0f}x{th:.0f}, área útil {iw:.0f}x{ih:.0f}"
                         " — alargue a figura ou quebre a linha")

    for i, a in enumerate(shapes):
        for b in shapes[i + 1:]:
            ba, bb = boxes[a["id"]], boxes[b["id"]]
            if overlap(ba, bb, 2) and not contains(ba, bb, 1) and not contains(bb, ba, 1):
                warns.append(f"sobreposição parcial: {label(a)} x {label(b)}")

    for ar in arrows:
        ends = {(ar.get(k) or {}).get("elementId") for k in ("startBinding", "endBinding")}
        pts = [(ar["x"] + p[0], ar["y"] + p[1]) for p in ar.get("points") or []]
        for k, end_pt in (("startBinding", pts[0] if pts else None), ("endBinding", pts[-1] if pts else None)):
            tid = (ar.get(k) or {}).get("elementId")
            if end_pt and tid in live and live[tid]["type"] in SHAPES:
                d = dist_to_box(end_pt, boxes[tid])
                if d > 20:
                    warns.append(f"{label(ar)}: ponta de {k} a {d:.0f}px de {label(live[tid])}")
        for s in shapes:
            if s["id"] in ends:
                continue
            b = boxes[s["id"]]
            if pts and (contains(b, (pts[0][0], pts[0][1], pts[0][0], pts[0][1]))
                        or contains(b, (pts[-1][0], pts[-1][1], pts[-1][0], pts[-1][1]))):
                continue  # figura que envolve uma das pontas: área/página, não obstáculo
            shrunk = (b[0] + 3, b[1] + 3, b[2] - 3, b[3] - 3)
            if any(seg_hits_box(p, q, shrunk) for p, q in zip(pts, pts[1:])):
                warns.append(f"{label(ar)} atravessa {label(s)} — desvie com pontos intermediários ou abra espaço")

    free = [t for t in texts if not t.get("containerId")]
    for t in free:
        tb = boxes[t["id"]]
        cx, cy = (tb[0] + tb[2]) / 2, (tb[1] + tb[3]) / 2
        hosts = [s for s in shapes if contains(boxes[s["id"]], (cx, cy, cx, cy))]
        if hosts:
            host = min(hosts, key=lambda s: (boxes[s["id"]][2] - boxes[s["id"]][0]) * (boxes[s["id"]][3] - boxes[s["id"]][1]))
            hb = boxes[host["id"]]
            others = [o for o in texts if o is not t and contains(hb, boxes[o["id"]], 2)]
            inner_shapes = [o for o in shapes if o is not host and contains(hb, boxes[o["id"]], 1)]
            if not others and not inner_shapes and not any(b.get("type") == "text" for b in host.get("boundElements") or []):
                warns.append(f"{label(t)} está solto dentro de {label(host)} — vincule com containerId")
            for s in shapes:
                if s is not host and overlap(tb, boxes[s["id"]], 1) and not contains(boxes[s["id"]], tb, 1) \
                        and not contains(tb, boxes[s["id"]], 1):
                    warns.append(f"{label(t)} invade a borda de {label(s)}")
            if not contains(hb, tb, 1):
                warns.append(f"{label(t)} vaza para fora de {label(host)}")
        elif len((t.get("text") or "").strip()) <= 12:
            for ar in arrows:
                pts = [(ar["x"] + p[0], ar["y"] + p[1]) for p in ar.get("points") or []]
                if any(math.hypot(cx - (p[0] + q[0]) / 2, cy - (p[1] + q[1]) / 2) < 45 for p, q in zip(pts, pts[1:])):
                    warns.append(f"{label(t)} parece rótulo de {label(ar)} — vincule com containerId na seta")
                    break

    # protótipo textual: controles escritos em texto em vez de desenhados
    for t in texts:
        if t.get("containerId"):
            continue
        hits = sum(len(rx.findall(t.get("text") or "")) for rx in TEXT_UI)
        if hits >= 2:
            warns.append(f"{label(t)} desenha controles em texto (botão entre colchetes, radio, caixa ASCII) — "
                         "protótipo textual; desenhe input, botão e radio como figuras")

    for i, a in enumerate(free):
        for b in free[i + 1:]:
            if overlap(boxes[a["id"]], boxes[b["id"]], 2):
                warns.append(f"textos sobrepostos: {label(a)} x {label(b)}")

    return errors, warns, fixed


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")  # console do Windows em cp1252
    sys.stderr.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", type=Path)
    ap.add_argument("--fix", action="store_true", help="acrescenta referências de volta e limpa entradas órfãs")
    ap.add_argument("--strict", action="store_true", help="avisos também falham")
    args = ap.parse_args()

    try:
        doc = json.loads(args.input.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        sys.exit(f"ERRO: JSON inválido: {e}")

    errors, warns, fixed = validate(doc, args.fix)
    if args.fix and fixed:
        args.input.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"--fix: {fixed} referência(s) corrigida(s) em boundElements")

    n = len([e for e in doc.get("elements", []) if not e.get("isDeleted")])
    for e in errors:
        print(f"ERRO  {e}")
    for w in warns:
        print(f"AVISO {w}")
    print(f"{n} elementos · {len(errors)} erro(s) · {len(warns)} aviso(s)")
    sys.exit(1 if errors or (args.strict and warns) else 0)


if __name__ == "__main__":
    main()
