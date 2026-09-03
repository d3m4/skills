"""Monta a pagina de decisoes a partir de um bloco em Markdown, JSON ou JSONL.

Uso:
  py gera_html.py <entrada.md|.json|.jsonl> <saida.html> [--gate NOME] [--todas] [--abrir]

Entrada:
  .jsonl  uma decisao por linha (o registro; ver SKILL.md). Por default so as
          com status "aberta" entram; --todas inclui as decididas (mostradas
          com a resposta ja marcada).
  .json   um array com o mesmo objeto.
  .md     o formato minimo abaixo. Tudo que nao for reconhecido vira contexto.

      ## dec-0001 — Titulo da decisao          (o id e opcional: "## Titulo" ganha d1, d2, ...)
      gate: etapa-1 · area: arquitetura · fonte: docs/x.md   (linha opcional de metadados)
      Contexto em um ou mais paragrafos.
      Impede: A2, A3                             (opcional)
      - a) texto da opcao — preco/consequencia
      - b) texto da opcao — preco/consequencia
      - c) texto da opcao — preco/consequencia
      Recomendação: b — o porque                 (obrigatoria; "Recomendacao" sem acento tambem vale)

--abrir abre no browser padrao. Codigo de saida 3 quando nao ha decisao a
mostrar: nada a decidir nao e erro, mas quem chama precisa saber.
"""
import json
import os
import re
import subprocess
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
OBRIGATORIOS = ("id", "titulo", "contexto", "opcoes", "recomendacao", "porque")

RE_TITULO = re.compile(r"^##\s+(?:([A-Za-z0-9_.\-]+)\s+[—–-]+\s+)?(.+?)\s*$")
RE_OPCAO = re.compile(r"^[-*]\s+\**([A-Za-z0-9]+)\)\**\s+(.*?)(?:\s+[—–]\s+(.*))?\s*$")
RE_REC = re.compile(r"^\**Recomenda[cç][aã]o\**\s*:\s*\**([A-Za-z0-9]+)\**\s*\.?\s*(?:[—–-]+\s*)?(.*)$", re.IGNORECASE)
RE_IMPEDE = re.compile(r"^\**Impede\**\s*:\s*(.*)$", re.IGNORECASE)
RE_META = re.compile(r"^(gate|area|área|fonte|criada)\s*:\s*", re.IGNORECASE)


def ler_md(caminho):
    blocos, atual = [], None
    for linha in open(caminho, encoding="utf-8").read().split("\n"):
        m = RE_TITULO.match(linha)
        if m:
            atual = {"id": m.group(1), "titulo": m.group(2), "contexto": [], "opcoes": [], "impede": []}
            blocos.append(atual)
            continue
        if atual is None:
            continue
        s = linha.strip()
        if not s:
            atual["contexto"].append("")
            continue
        m = RE_OPCAO.match(s)
        if m:
            atual["opcoes"].append({"id": m.group(1), "texto": m.group(2).strip(), "preco": (m.group(3) or "").strip()})
            continue
        m = RE_REC.match(s)
        if m:
            atual["recomendacao"], atual["porque"] = m.group(1), m.group(2).strip()
            continue
        m = RE_IMPEDE.match(s)
        if m:
            atual["impede"] = [x.strip() for x in re.split(r"[,;]", m.group(1)) if x.strip()]
            continue
        if RE_META.match(s):
            for par in re.split(r"\s*[·;|]\s*", s):
                k, _, v = par.partition(":")
                k = k.strip().lower().replace("área", "area")
                if k in ("gate", "area", "fonte", "criada"):
                    atual[k] = v.strip()
            continue
        atual["contexto"].append(s)
    saida = []
    for n, b in enumerate(blocos, 1):
        b["id"] = b["id"] or f"d{n}"
        b["contexto"] = re.sub(r"\n{3,}", "\n\n", "\n".join(b["contexto"])).strip()
        b.setdefault("status", "aberta")
        saida.append(b)
    return saida


def ler_jsonl(caminho):
    saida = []
    with open(caminho, encoding="utf-8") as f:
        for n, linha in enumerate(f, 1):
            if linha.strip():
                try:
                    saida.append(json.loads(linha))
                except json.JSONDecodeError as e:
                    sys.exit(f"{caminho}:{n}: JSON invalido: {e}")
    return saida


def carregar(caminho):
    ext = os.path.splitext(caminho)[1].lower()
    if ext == ".jsonl":
        return ler_jsonl(caminho)
    if ext == ".json":
        dados = json.load(open(caminho, encoding="utf-8"))
        return dados if isinstance(dados, list) else [dados]
    if ext in (".md", ".markdown", ".txt"):
        return ler_md(caminho)
    sys.exit(f"extensao nao suportada: {ext} (use .md, .json ou .jsonl)")


def validar(decisoes, origem):
    vistos = set()
    for d in decisoes:
        faltam = [c for c in OBRIGATORIOS if not d.get(c) and d.get(c) != ""]
        if "porque" in faltam and d.get("recomendacao"):
            faltam.remove("porque")
        if faltam:
            sys.exit(f"{origem}: decisao {d.get('id')!r} ({d.get('titulo')!r}) sem {faltam}")
        ids = [o.get("id") for o in d["opcoes"]]
        if len(ids) < 2:
            sys.exit(f"{origem}: decisao {d['id']} tem {len(ids)} opcao(oes); o minimo e 2")
        if d["recomendacao"] not in ids:
            sys.exit(f"{origem}: decisao {d['id']}: recomendacao {d['recomendacao']!r} nao esta em {ids}")
        if d["id"] in vistos:
            sys.exit(f"{origem}: id duplicado {d['id']}")
        vistos.add(d["id"])
        d.setdefault("status", "aberta")
        d.setdefault("gate", "-")
        d.setdefault("area", "-")
        d.setdefault("criada", "")
        d.setdefault("porque", "")
        d.setdefault("impede", [])


def main(argv):
    if len(argv) < 3:
        sys.exit(__doc__)
    entrada, saida = argv[1], argv[2]
    gate, todas, abrir = None, False, False
    i = 3
    while i < len(argv):
        if argv[i] == "--gate":
            gate, i = argv[i + 1], i + 2
        elif argv[i] == "--todas":
            todas, i = True, i + 1
        elif argv[i] == "--abrir":
            abrir, i = True, i + 1
        else:
            sys.exit(f"argumento desconhecido: {argv[i]}")
    decisoes = carregar(entrada)
    validar(decisoes, entrada)
    mostrar = [d for d in decisoes if (todas or d["status"] == "aberta") and (gate is None or d.get("gate") == gate)]
    template = open(os.path.join(AQUI, "template.html"), encoding="utf-8").read()
    ini, fim = "/*DADOS*/", "/*FIM*/"
    a, b = template.index(ini), template.index(fim) + len(fim)
    dados = json.dumps(mostrar, ensure_ascii=False).replace("</", "<\\/")
    os.makedirs(os.path.dirname(os.path.abspath(saida)) or ".", exist_ok=True)
    with open(saida, "w", encoding="utf-8", newline="\n") as f:
        f.write(template[:a] + ini + dados + fim + template[b:])
    print(f"{len(mostrar)} de {len(decisoes)} decisao(oes) -> {saida}")
    if abrir and mostrar:
        alvo = os.path.abspath(saida)
        if sys.platform.startswith("win"):
            os.startfile(alvo)  # noqa: S606
        elif sys.platform == "darwin":
            subprocess.Popen(["open", alvo])
        else:
            subprocess.Popen(["xdg-open", alvo])
    return 0 if mostrar else 3


if __name__ == "__main__":
    sys.exit(main(sys.argv))
