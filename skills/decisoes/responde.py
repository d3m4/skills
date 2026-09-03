"""Aplica as respostas coladas pelo dono ao decisoes.jsonl.

Uso:
  py responde.py <decisoes.jsonl> <respostas.txt> [--data AAAA-MM-DD]
  py responde.py <decisoes.jsonl> - < respostas.txt

Formato das respostas (o que o botao "Copiar respostas" do HTML monta):
  respostas as questoes do jsonl pendentes
  dec-0001: b — complemento livre
  dec-0002: a
  dec-0003: outra — descricao da escolha

Regras: id desconhecido, decisao ja decidida ou opcao inexistente ABORTAM sem
gravar nada (o arquivo so e reescrito quando todas as linhas sao validas).
"(sem resposta)" pula a decisao, que continua aberta. A ordem das linhas do
JSONL e preservada; so os campos status/resposta/complemento/decidida_em das
decisoes respondidas mudam.
"""
import datetime
import json
import re
import sys

LINHA = re.compile(r"^\s*([A-Za-z0-9_.\-]+)\s*:\s*([^\s—-]+|\(sem resposta\))\s*(?:[—-]+\s*(.*))?$")


def main(argv):
    if len(argv) < 3:
        sys.exit(__doc__)
    caminho, respostas = argv[1], argv[2]
    data = datetime.date.today().isoformat()
    if "--data" in argv:
        data = argv[argv.index("--data") + 1]
    texto = sys.stdin.read() if respostas == "-" else open(respostas, encoding="utf-8").read()

    linhas_brutas = [l for l in texto.splitlines() if l.strip()]
    if not linhas_brutas:
        sys.exit("respostas vazias")
    if linhas_brutas[0].strip().lower().startswith("respostas as questoes"):
        linhas_brutas = linhas_brutas[1:]

    respostas_por_id = {}
    for l in linhas_brutas:
        m = LINHA.match(l)
        if not m:
            sys.exit(f"linha nao entendida: {l!r}")
        did, opcao, comp = m.group(1), m.group(2), (m.group(3) or "").strip()
        if opcao == "(sem resposta)":
            continue
        if did in respostas_por_id:
            sys.exit(f"id repetido nas respostas: {did}")
        respostas_por_id[did] = (opcao, comp)

    with open(caminho, encoding="utf-8") as f:
        originais = [l for l in f.read().split("\n")]
    docs = []
    for n, l in enumerate(originais, 1):
        if not l.strip():
            docs.append((l, None))
            continue
        try:
            docs.append((l, json.loads(l)))
        except json.JSONDecodeError as e:
            sys.exit(f"{caminho}:{n}: JSON invalido: {e}")

    por_id = {d["id"]: d for _, d in docs if d is not None}
    for did, (opcao, comp) in respostas_por_id.items():
        if did not in por_id:
            sys.exit(f"id desconhecido: {did}")
        d = por_id[did]
        if d.get("status") != "aberta":
            sys.exit(f"{did} nao esta aberta (status {d.get('status')!r})")
        ids = [o["id"] for o in d["opcoes"]]
        if opcao != "outra" and opcao not in ids:
            sys.exit(f"{did}: opcao {opcao!r} nao existe (opcoes: {ids} ou 'outra')")
        if opcao == "outra" and not comp:
            sys.exit(f"{did}: 'outra' exige complemento descrevendo a escolha")

    aplicadas = []
    saida = []
    for l, d in docs:
        if d is None or d["id"] not in respostas_por_id:
            saida.append(l)
            continue
        opcao, comp = respostas_por_id[d["id"]]
        d["status"] = "decidida"
        d["resposta"] = opcao
        d["complemento"] = comp or None
        d["decidida_em"] = data
        saida.append(json.dumps(d, ensure_ascii=False))
        aplicadas.append((d["id"], opcao, comp))

    with open(caminho, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(saida))
        if not saida[-1].endswith("\n") and saida[-1] != "":
            f.write("\n")

    for did, opcao, comp in aplicadas:
        print(f"{did}: {opcao}" + (f" — {comp}" if comp else ""))
    abertas = sum(1 for _, d in docs if d is not None and d["status"] == "aberta")
    print(f"{len(aplicadas)} decidida(s); {abertas} continuam abertas")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
