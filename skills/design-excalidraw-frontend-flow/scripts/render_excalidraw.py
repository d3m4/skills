"""Renderiza um .excalidraw em PNG para conferência visual.

Uso:
    python render_excalidraw.py <arquivo.excalidraw> [--out arquivo.png] [--scale 1]
    python render_excalidraw.py <arquivo.excalidraw> --crop X Y W H     # recorte em coordenadas da cena
    python render_excalidraw.py <arquivo.excalidraw> --tiles 1600x1200  # fatia o canvas inteiro

Canvas grande vira uma imagem miniatura ilegível quando aberta inteira. Use o PNG
completo para julgar a composição e --crop/--tiles para ler textos e conferir setas.

Requisitos (uma vez):
    python -m pip install --user playwright
O navegador usado é o Edge ou o Chrome já instalados. Só se nenhum existir:
    python -m playwright install chromium

O Excalidraw é carregado do esm.sh, então o render precisa de internet.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

PADDING = 40  # igual ao exportPadding do render_template.html


def scene_bounds(elements: list[dict]) -> tuple[float, float, float, float]:
    min_x = min_y = math.inf
    max_x = max_y = -math.inf
    for el in elements:
        x, y = el.get("x", 0), el.get("y", 0)
        if el.get("type") in ("arrow", "line", "freedraw") and el.get("points"):
            pts = [(x + px, y + py) for px, py in el["points"]]
        else:
            w, h = el.get("width", 0), el.get("height", 0)
            pts = [(x, y), (x + w, y + h)]
        for px, py in pts:
            min_x, min_y = min(min_x, px), min(min_y, py)
            max_x, max_y = max(max_x, px), max(max_y, py)
    if min_x == math.inf:
        return 0, 0, 800, 600
    return min_x, min_y, max_x, max_y


def launch(p):
    for channel in ("msedge", "chrome", None):
        try:
            return p.chromium.launch(headless=True, channel=channel) if channel else p.chromium.launch(headless=True)
        except Exception:
            continue
    sys.exit("ERRO: nenhum navegador disponível. Rode: python -m playwright install chromium")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")  # console do Windows em cp1252
    sys.stderr.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", type=Path)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--scale", type=float, default=1.0, help="fator de pixel (2 = nítido, arquivo maior)")
    ap.add_argument("--crop", type=float, nargs=4, metavar=("X", "Y", "W", "H"))
    ap.add_argument("--tiles", metavar="LxA", help="fatia o canvas em pedaços de LxA unidades da cena")
    args = ap.parse_args()

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit("ERRO: playwright ausente. Rode: python -m pip install --user playwright")

    data = json.loads(args.input.read_text(encoding="utf-8"))
    if data.get("type") != "excalidraw" or not data.get("elements"):
        sys.exit("ERRO: o arquivo não é uma cena Excalidraw com elementos.")
    elements = [e for e in data["elements"] if not e.get("isDeleted")]
    min_x, min_y, max_x, max_y = scene_bounds(elements)
    width = int(max_x - min_x + 2 * PADDING) + 1
    height = int(max_y - min_y + 2 * PADDING) + 1

    template = (Path(__file__).parent / "render_template.html").as_uri()
    base = args.out or args.input.with_suffix(".png")
    written: list[Path] = []

    with sync_playwright() as p:
        browser = launch(p)
        page = browser.new_page(viewport={"width": min(width, 4000), "height": min(height, 4000)},
                                device_scale_factor=args.scale)
        page.goto(template, wait_until="commit")
        page.wait_for_function("window.__moduleReady === true", timeout=120000)
        result = page.evaluate("d => window.renderDiagram(d)", data)
        if not result.get("success"):
            browser.close()
            sys.exit(f"ERRO no render: {result.get('error')}")
        # a estimativa local serve só para dimensionar a janela; o recorte usa os limites do Excalidraw
        min_x, min_y, max_x, max_y = result["bounds"]
        width, height = result["width"], result["height"]

        def shot(path: Path, sx: float, sy: float, sw: float, sh: float) -> None:
            # converte coordenadas da cena em pixels CSS do SVG exportado
            cx, cy = max(sx - min_x + PADDING, 0), max(sy - min_y + PADDING, 0)
            cw, ch = min(sw, width - cx), min(sh, height - cy)
            if cw <= 0 or ch <= 0:
                return
            page.screenshot(path=str(path), full_page=True,
                            clip={"x": cx, "y": cy, "width": cw, "height": ch})
            written.append(path)

        if args.crop:
            shot(base, *args.crop)
        elif args.tiles:
            tw, th = (float(v) for v in args.tiles.lower().split("x"))
            # sobra menor que 10% da fatia é só margem: não vira fatia própria
            rows = max(1, math.ceil(height / th - 0.1))
            cols = max(1, math.ceil(width / tw - 0.1))
            for r in range(rows):
                for c in range(cols):
                    sx, sy = min_x - PADDING + c * tw, min_y - PADDING + r * th
                    # a última linha/coluna absorve a sobra (shot limita ao fim do canvas)
                    sw = tw if c < cols - 1 else width
                    sh = th if r < rows - 1 else height
                    out = base.with_name(f"{base.stem}.tile-{r + 1}-{c + 1}.png")
                    shot(out, sx, sy, sw, sh)
                    print(f"{out}  (cena x={sx:.0f} y={sy:.0f})")
        else:
            page.locator("#root svg").screenshot(path=str(base))
            written.append(base)
        browser.close()

    if not args.tiles:
        for path in written:
            print(path)
    print(f"cena: x {min_x:.0f}..{max_x:.0f}  y {min_y:.0f}..{max_y:.0f}", file=sys.stderr)


if __name__ == "__main__":
    main()
