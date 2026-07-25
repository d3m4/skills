---
name: htmlize
description: Use quando o usuário quer transformar um markdown/doc/conteúdo num infográfico HTML clean e responsivo (PicoCSS + Bootstrap Icons), tema escuro, self-contained, com sumário lateral e barra de progresso, e abrir no navegador automaticamente. Trigger: /htmlize
---

Transforme o conteúdo em `$ARGUMENTS` (um arquivo markdown/doc, ou texto colado) num **infográfico HTML self-contained e responsivo** e abra no navegador automaticamente.

## Workflow obrigatório

1. Leia o conteúdo de entrada (arquivo ou texto). Se for um caminho, leia o arquivo.
2. Identifique a estrutura: título, seções, números/estatísticas, listas, etapas/fases, pontos críticos, blocos de código.
3. Mapeie cada parte para os componentes da receita (use `template.html` como esqueleto — ele já traz todo o CSS, o layout responsivo, o sumário e o script prontos).
4. Dê um `id` em kebab-case a cada `<section>` e gere **um link no sumário lateral por seção**.
5. Gere **um único arquivo `.html`** com todo o CSS inline em `<style>` — sem build, sem dependências locais.
6. Abra automaticamente no navegador (variações por SO abaixo).
7. Informe ao usuário o caminho do arquivo gerado.

## Receita do "estilo htmlize"

- **CDNs (sempre via `<link>` no `<head>`)**:
  - PicoCSS: `https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css`
  - Bootstrap Icons: `https://cdn.jsdelivr.net/npm/bootstrap-icons@1.13.1/font/bootstrap-icons.min.css`
- **Tema**: escuro por padrão (`<html data-theme="dark">`). Accent azul `#5e9eff` (`--accent`) e verde `#7ee0c0` (`--accent-2`). Auxiliares: `--warn #ffb454`, `--danger #ff7b72`, `--good #7ee0c0`.
- **Fonte**: Inter / system-ui.
- **Conteúdo em pt-BR** por padrão.
- **Um único arquivo**: CSS inline em `<style>`, script inline em `<script>`. Nunca gere arquivos auxiliares (.css, .js).

## Responsividade (obrigatória — celular, tablet e PC)

Mobile-first com largura fluida + media queries. Não trave o conteúdo numa largura fixa pequena:

- **Largura fluida**: o wrapper usa `width: min(1320px, 92vw)` (`.wrap`) por padrão — aproveita quase toda a tela em monitores médios e respira nas bordas em telas menores.
- **Largura de leitura**: o texto corrido (`<p>`) fica limitado a `--reading: 72ch` (~65–75 caracteres/linha) mesmo quando o layout é largo. Os grids (stats, cards, timeline) ocupam a largura inteira.
- **A válvula de escape é `.full` (ou `.nota`)**: o limite acima vale para *texto corrido*, não para tudo que é `<p>`. Nota de rodapé, legenda e qualquer parágrafo que **acompanha um elemento largo** (tabela, grid, imagem) precisa de `.full` ou `.nota` — senão vira uma coluna estreita colada num bloco largo, e fica feio.
- **Listas acompanham o container, não a largura de leitura.** Nunca limite `<ul>`/`<ol>` a `--reading`: uma lista de itens substantivos com 72ch deixa um vazio enorme à direita em monitor largo. O template já trata isso.
- **Tipografia fluida**: títulos e números grandes usam `clamp()` para escalar entre mínimo e máximo sem saltos.
- **Grids intrínsecos**: `repeat(auto-fit, minmax(min(100%, 280px), 1fr))` — viram mais colunas em telas largas e empilham no celular, sem media query por grid.
- **Breakpoints**: `≥1100px` ativa o sumário lateral; `≥1600px` (telas grandes / 1440p+) sobe o teto para `--maxw: 1760px`, usa `95vw` e alarga o sumário (`--toc-w: 250px`) para reduzir as margens horizontais e aproveitar o real estate; `≤560px` reduz paddings. Use `viewport-fit=cover` no `<meta viewport>`.

## Sumário lateral + barra de progresso (obrigatórios)

- **Barra de progresso**: `<div class="progress">` fixa no topo, preenchida via o script inline conforme o scroll.
- **Sumário (TOC) lateral**: `<aside class="toc">` com um `<a href="#id">` por seção. Fica **sticky à direita no desktop** e **some automaticamente abaixo de 1100px** (tablet/celular) — nunca deve atrapalhar a leitura em telas menores.
- O script inline destaca o link da seção visível (IntersectionObserver). Toda `<section>` precisa ter `id`, e o texto do link deve bater com o `<h2>` da seção.

## Checklist de seções (use as que o conteúdo pedir)

- [ ] **Hero**: gradiente radial azul/verde, `<h1>` com ícone, subtítulo `.sub`, e `.pills` de metadados (data, status, stack/tags). Use `.pill.ok` para status positivo.
- [ ] **Kicker**: todo `<h2>` de seção vem dentro de `.kicker` (ícone Bootstrap + h2).
- [ ] **Stats**: cards `.stat` (número grande `.num` + `.lbl`). Variantes `.num.warn` / `.num.danger`.
- [ ] **Grid de cards**: `.grid-cards` com `.card` (h3 com ícone + parágrafo). `.card.solved` (borda verde) para itens resolvidos/positivos.
- [ ] **Decisão/versus** (opcional): `.decision` com `.versus` e `.opt.win` / `.opt.no`.
- [ ] **Tabela**: **sempre** dentro de `<div class="tabela">`, que dá `overflow-x: auto`. Sem o wrapper, uma tabela larga estoura a viewport no celular e o `<body>` inteiro passa a rolar na horizontal. Nota de rodapé da tabela usa `<p class="nota">`.
- [ ] **Código**: `<pre><code>…</code></pre>`.
- [ ] **Callout**: `.callout` para pontos críticos (vermelho). Variantes `.callout.ok` (verde) e `.callout.warn` (amarelo).
- [ ] **Timeline**: `.timeline` vertical com `.phase`; itens em `.slices` com `<code>` de numeração (`1.0`, `2.1`…).
- [ ] **Rodapé**: `.muted-foot` com proveniência (arquivo de origem + crédito "PicoCSS + Bootstrap Icons").

## Mapeamento de conteúdo → componente

| No conteúdo de entrada | Vira |
|------------------------|------|
| Título / H1 | Hero |
| Métricas, percentuais, "X GB", contagens | Stats |
| Lista de features/objeções/itens | Grid de cards |
| Comparação de opções/alternativas | Decisão + versus |
| Passos numerados, roadmap, fases | Timeline |
| Aviso, risco, "atenção", "crítico" | Callout |
| Tabela markdown | `.tabela` + `<table>` (wrapper obrigatório) |
| Nota de rodapé de tabela († ‡ *) | `<p class="nota">` — uma por marcador |
| Bloco de código / structs / config | `<pre><code>` |

Escolha ícones do Bootstrap Icons coerentes com o tema de cada seção (`bi-exclamation-triangle-fill` para riscos, `bi-lightbulb-fill` para ideias, `bi-diagram-3-fill` para planos, etc.).

## Abrir no navegador (variação por SO)

Detecte o SO e rode o comando correspondente após gerar o arquivo:

- **Windows**: `Start-Process "caminho\arquivo.html"`
- **macOS**: `open "caminho/arquivo.html"`
- **Linux**: `xdg-open "caminho/arquivo.html"`

## Regras

- Nunca use build tools, frameworks JS ou bundlers — é HTML puro + 2 CDNs + um script inline mínimo.
- Não invente dados: só use o que está no conteúdo de entrada. Se faltar metadado (data, autor), omita a pill em vez de inventar.
- Preserve a semântica e os números do original — você só reorganiza visualmente.
- Toda seção precisa de `id` e de um link correspondente no sumário.
- Nome do arquivo de saída: derive do título (kebab-case) + `.html`, no mesmo diretório do arquivo de origem (ou no diretório atual se for texto colado).
- **Nunca deixe markdown cru vazar para a tela.** Antes de abrir no navegador, procure `**`, `` ` `` e `|---` sobrando no HTML — se houver, a conversão falhou em algum ponto e o usuário vai ver os asteriscos.
- **Negrito envolvendo código (`` **`x`** ``) é a armadilha clássica.** Se você extrair os trechos de `` ` `` antes de aplicar o negrito, o par `**` fica em pedaços diferentes e nunca casa. Ordem correta: troque o código por um marcador, aplique negrito/itálico/links no texto inteiro, e só então devolva o código. O mesmo vale para negrito atravessando um link.

## Quando o conteúdo é longo (vários arquivos ou > ~500 linhas)

Converter à mão parágrafo por parágrafo perde trecho e não escala. Nesses casos **escreva um pequeno conversor em Python (stdlib)** que lê os arquivos e emite o HTML, e deixe o script junto do resultado:

- Um HTML derivado sem o script que o gerou **envelhece na primeira vez que a fonte muda**, e ninguém percebe.
- O script permite verificar a completude: compare a contagem de seções da fonte com a do HTML e falhe se faltar alguma.
- Reaproveite o CSS e o script deste `template.html` lendo-o em tempo de geração, mas **degrade sem ele** — nunca fixe um caminho absoluto de perfil de usuário no script versionado.
