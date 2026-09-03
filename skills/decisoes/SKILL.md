---
name: decisoes
description: Use when a task raises a question only the owner can answer (design choice, scope, policy, value) and the work should continue instead of stopping to ask; when a gate closes with pending decisions; or when the owner hands over a block of decisions in Markdown or JSONL and wants a single page to answer them all at once. Trigger: /decisoes
---

# Decisões em lote

Decisão que só o dono toma **não interrompe o trabalho**: vira uma entrada no
registro, o resto segue, e no fechamento do gate todas as pendentes viram uma
página HTML que ele responde de uma vez e cola de volta no terminal.

## Quando usar

- Apareceu uma escolha que muda o desenho e não está no pedido nem no código
  (dois caminhos válidos, valor que só o dono conhece, política de produto).
- O gate fechou (o pacote combinado acabou; o que sobrou está impedido) e há
  pendentes para o dono.
- O dono entregou um bloco de decisões (`.md` ou `.jsonl`) e quer a página.
- O dono colou o texto `respostas as questoes do jsonl pendentes`.

**Não** usar para dúvida que o código, o repositório ou uma convenção já
respondem: isso se resolve lendo, não perguntando.

## O ciclo

1. **Registrar, não perguntar.** No momento em que a dúvida aparece, uma linha
   nova no `decisoes.jsonl` do projeto (caminho abaixo). Contexto suficiente
   para decidir sem abrir o código; **três opções** com preço; a recomendação
   e o porquê; o que ela impede. Depois, executar tudo que **não depende**
   dela. Parar só quando o que sobrou está todo impedido.
2. **Fechar o gate.** Gerar a página com as abertas e abrir no browser:
   ```bash
   py ~/.claude/skills/decisoes/gera_html.py <registro.jsonl|bloco.md> <saida.html> --abrir
   ```
   Saída versionada ao lado do registro: `docs/decisoes/pendentes-AAAA-MM-DD.html`.
   Código de saída 3 = nada aberto, não gerar nem anunciar página.
3. **Receber as respostas.** O dono cola o texto do botão "Copiar respostas".
   Gravar num arquivo temporário e aplicar:
   ```bash
   py ~/.claude/skills/decisoes/responde.py <registro.jsonl> <respostas.txt>
   ```
   O script aborta inteiro em id desconhecido, decisão já decidida ou opção
   inexistente; nada é gravado pela metade. Depois, executar o que destravou e
   citar o id da decisão no commit.

Bloco em Markdown que o dono entregar sem registro: gerar a página direto
dele (o gerador lê `.md`); só criar linhas no JSONL se ele mandar registrar.

## Onde fica o registro

`docs/decisoes.jsonl` na raiz do projeto, salvo indicação no `AGENTS.md`.
Append-only e em ordem: linha nova vai ao fim; decidir muda só os campos
`status`, `resposta`, `complemento` e `decidida_em` da própria linha. Ids
sequenciais `dec-NNNN`; nunca reaproveitar.

## O registro, campo a campo

```json
{"id":"dec-0012","status":"aberta","criada":"2026-09-03","gate":"etapa-1-pre-separacao",
 "area":"arquitetura","titulo":"session/commands.ts como raiz de composição",
 "contexto":"A spec de 02/09 negava; o código lista em wiring.ts::RAIZES_DE_COMPOSICAO.",
 "opcoes":[{"id":"a","texto":"manter como raiz","preco":"objeção fica sem resposta"},
           {"id":"b","texto":"tirar da lista","preco":"AGENTS.md, wiring.ts e teste no mesmo commit"},
           {"id":"c","texto":"manter e escrever o porquê","preco":"uma frase no AGENTS.md"}],
 "recomendacao":"c","porque":"a lista do código está certa na prática; falta o motivo escrito.",
 "impede":["C4 fatia 0b"],"fonte":"wd3/docs/specs/melhoria-arquitetura-2026-08-30.md",
 "resposta":null,"complemento":null,"decidida_em":null}
```

`status` é `aberta` ou `decidida`. `resposta` é o id da opção ou `outra`
(aí `complemento` descreve a escolha). `impede` nomeia itens de trabalho, não
frases. O formato Markdown equivalente está no cabeçalho de `gera_html.py`.

## Formato das respostas

```text
respostas as questoes do jsonl pendentes
dec-0012: c — e cite o motivo também no README do wiring
dec-0013: a
dec-0014: outra — as duas primeiras opções juntas
```

## Erros comuns

| erro | correção |
|---|---|
| Parar e perguntar no terminal | Registrar e seguir; a pergunta no terminal só quando **tudo** que sobrou está impedido |
| Opções que são a mesma coisa em três tons | Cada opção tem preço diferente; se só há um caminho, não é decisão, é execução |
| Contexto que manda "ver o arquivo X" | O dono responde do browser; o contexto tem de bastar sozinho |
| Executar assumindo a recomendação sem registrar | Se avançou na recomendação, a entrada diz isso em `contexto` e o retrabalho é conhecido |
| Editar o JSONL à mão para marcar decidida | Só `responde.py`; ele valida e preserva a ordem |
| Gerar página com zero pendentes | Código 3 do gerador: não há o que decidir, não há página |
