"""Converte um canvas legado (setas e rótulos soltos) em canvas ligado.

Uso:
    python bind_loose.py <entrada.excalidraw> [--out saida.excalidraw] [--dry-run]

O que faz, sem mover figuras:
  - seta sem binding: liga cada ponta à figura cuja borda está a até 20px dela
    (empate: a menor figura) e registra a seta no boundElements da figura;
  - texto solto que é o único conteúdo de uma figura vira rótulo vinculado
    (containerId + boundElements). Texto centralizado continua centralizado;
    texto encostado à esquerda (placeholder de input) continua à esquerda;
  - texto curto solto (até 12 caracteres, ex. Sim/Não) perto do meio de uma
    seta vira rótulo da seta e é reposicionado sobre ela.

Figuras que contêm várias coisas (página, card, seção) não recebem rótulo:
o texto dentro delas é título/conteúdo e continua solto. Rode depois o
validate_excalidraw.py e o render para conferir.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from validate_excalidraw import PAD, SHAPES, bbox, contains, dist_to_box, text_size  # noqa: E402

SNAP = 20


def area(b) -> float:
    return (b[2] - b[0]) * (b[3] - b[1])


def polyline_mid(pts):
    """Ponto no meio do comprimento da seta, onde o Excalidraw põe o rótulo."""
    segs = [(p, q, math.dist(p, q)) for p, q in zip(pts, pts[1:])]
    half = sum(s[2] for s in segs) / 2
    for p, q, d in segs:
        if half <= d and d > 0:
            t = half / d
            return p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t
        half -= d
    return pts[-1]


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", type=Path)
    ap.add_argument("--out", type=Path, help="padrão: sobrescreve a entrada")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    doc = json.loads(args.input.read_text(encoding="utf-8"))
    live = [e for e in doc["elements"] if not e.get("isDeleted")]
    by_id = {e["id"]: e for e in live}
    shapes = [e for e in live if e["type"] in SHAPES]
    texts = [e for e in live if e["type"] == "text"]
    arrows = [e for e in live if e["type"] == "arrow"]
    box = {e["id"]: bbox(e) for e in live}

    def link(owner: dict, child: dict) -> None:
        be = owner.get("boundElements") or []
        if not any(b.get("id") == child["id"] for b in be):
            owner["boundElements"] = be + [{"type": child["type"], "id": child["id"]}]

    n_ends = n_labels = n_arrow_labels = 0
    misses: list[str] = []

    # 1. pontas de seta
    for ar in arrows:
        pts = [(ar["x"] + p[0], ar["y"] + p[1]) for p in ar.get("points") or []]
        if len(pts) < 2:
            continue
        for key, pt in (("startBinding", pts[0]), ("endBinding", pts[-1])):
            if (ar.get(key) or {}).get("elementId") in by_id:
                continue
            cands = [(abs(dist_to_box(pt, box[s["id"]])), area(box[s["id"]]), s) for s in shapes]
            cands = [c for c in cands if c[0] <= SNAP]
            if not cands:
                misses.append(f'seta "{ar["id"]}": nenhuma figura perto da ponta {key}')
                continue
            d, _, target = min(cands, key=lambda c: (round(c[0] / 4), c[1]))
            ar[key] = {"elementId": target["id"], "focus": 0, "gap": max(round(d), 1)}
            link(target, ar)
            n_ends += 1

    # 2. rótulos de figura
    taken = {e["containerId"] for e in texts if e.get("containerId")}
    for t in texts:
        if t.get("containerId"):
            continue
        tb = box[t["id"]]
        cx, cy = (tb[0] + tb[2]) / 2, (tb[1] + tb[3]) / 2
        hosts = [s for s in shapes if contains(box[s["id"]], (cx, cy, cx, cy))]
        if not hosts:
            continue
        host = min(hosts, key=lambda s: area(box[s["id"]]))
        hb = box[host["id"]]
        crowded = any(o is not t and contains(hb, box[o["id"]], 2) for o in texts) or \
            any(o is not host and contains(hb, box[o["id"]], 1) for o in shapes)
        if crowded or host["id"] in taken:
            continue
        w, h = text_size(t)
        hcx = (hb[0] + hb[2]) / 2
        # mantém o alinhamento de quem desenhou: botão centralizado, placeholder à esquerda
        centered = t.get("textAlign") == "center"
        t.update(containerId=host["id"], verticalAlign="middle",
                 width=round(w, 2), height=round(h, 2),
                 x=round(hcx - w / 2 if centered else max(tb[0], hb[0] + PAD), 2),
                 y=round((hb[1] + hb[3]) / 2 - h / 2, 2))
        link(host, t)
        taken.add(host["id"])
        n_labels += 1

    # 3. rótulos de seta (Sim / Não)
    labelled = {e["containerId"] for e in texts if e.get("containerId")}
    for t in texts:
        if t.get("containerId") or len((t.get("text") or "").strip()) > 12:
            continue
        tb = box[t["id"]]
        cx, cy = (tb[0] + tb[2]) / 2, (tb[1] + tb[3]) / 2
        if any(contains(box[s["id"]], (cx, cy, cx, cy)) for s in shapes):
            continue
        best = None
        for ar in arrows:
            if ar["id"] in labelled:
                continue
            pts = [(ar["x"] + p[0], ar["y"] + p[1]) for p in ar.get("points") or []]
            for p, q in zip(pts, pts[1:]):
                d = math.hypot(cx - (p[0] + q[0]) / 2, cy - (p[1] + q[1]) / 2)
                if d < 45 and (best is None or d < best[0]):
                    best = (d, ar, pts)
        if not best:
            continue
        _, ar, pts = best
        mx, my = polyline_mid(pts)
        w, h = text_size(t)
        t.update(containerId=ar["id"], textAlign="center", verticalAlign="middle",
                 width=round(w, 2), height=round(h, 2), x=round(mx - w / 2, 2), y=round(my - h / 2, 2))
        link(ar, t)
        labelled.add(ar["id"])
        n_arrow_labels += 1

    print(f"pontas de seta ligadas: {n_ends} · rótulos de figura: {n_labels} · rótulos de seta: {n_arrow_labels}")
    for m in misses:
        print(f"SEM PAR {m}")
    if not args.dry_run:
        out = args.out or args.input
        out.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
        print(out.resolve())


if __name__ == "__main__":
    main()
