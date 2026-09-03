# skills

Skills portáteis para agentes de IA (Claude Code, Codex e similares). Cada skill é um arquivo de instruções (`SKILL.md`) autocontido — copie para o diretório de skills do seu agente e use.

## Skills disponíveis

| Skill | O que faz | Trigger |
|-------|-----------|---------|
| [`htmlize`](skills/htmlize/) | Transforma um markdown/doc/conteúdo num infográfico HTML clean e responsivo (PicoCSS + Bootstrap Icons), tema escuro, com sumário lateral e barra de progresso, e abre no navegador. | `/htmlize` |
| [`discuta-comigo`](skills/discuta-comigo/) | Refina uma ideia, decisão ou problema junto com você em rodadas de 4 perguntas de múltipla escolha, perguntando ao fim de cada rodada se deve continuar perguntando ou já propor — só apresenta a proposta quando você libera. | `/discuta-comigo` |
| [`notes-tarefas`](skills/notes-tarefas/) | Organiza notas/tarefas enviadas no chat no sistema tarefas/ do repositório de notas — classifica entre task (todo/rotina) ou ideia (pasta temática), pergunta categoria se necessário, e faz commit+push. | enviar nota no chat |

---

## discuta-comigo

Em vez de uma resposta imediata, conduz uma **conversa estruturada de descoberta**: você passa a pergunta/tema inicial e o agente faz **rodadas de 4 perguntas de múltipla escolha** (foco em propósito, restrições, critérios e trade-offs, cada uma liderada por uma recomendação). Ao fim de **toda** rodada, vem a **pergunta-ponte**: mais 4 perguntas ou já propor? Só depois que você libera é que ele apresenta o desenho fechado (2–3 abordagens com trade-offs e recomendação). Ótimo pra clarear requisitos antes de qualquer implementação.

- `skills/discuta-comigo/SKILL.md` — o instruction file (o processo completo).

### Exemplo de uso

```
/discuta-comigo quero montar um home lab para estudar kubernetes
```

ou em linguagem natural:

```
discuta comigo: qual stack usar pra um SaaS de notas fiscais?
```

O agente analisa o contexto disponível, faz a primeira rodada de 4 perguntas e segue refinando até você pedir a proposta.

---

## htmlize

Pega um arquivo markdown, doc ou conteúdo colado e gera **um único arquivo `.html`** — infográfico clean, tema escuro, com hero, cards de estatística, grid de cards, timeline, callouts e blocos de código. Totalmente **responsivo** (celular, tablet e PC): largura fluida `min(1320px, 92vw)` que aproveita monitores grandes (1440p) sem esticar demais o texto (limitado a ~72 caracteres/linha), tipografia fluida com `clamp()`, **sumário lateral** sticky que some em telas estreitas e **barra de progresso** de leitura. Sem build: só PicoCSS + Bootstrap Icons via CDN, CSS e um script mínimo inline. Abre no navegador automaticamente.

- `skills/htmlize/SKILL.md` — o instruction file (a "receita" do estilo).
- `skills/htmlize/template.html` — esqueleto pronto com todo o CSS e seções placeholder.

### Exemplo de uso

```
/htmlize docs/meu-documento.md
```

ou em linguagem natural:

```
htmlize esse arquivo: docs/meu-documento.md
```

O agente lê o conteúdo, mapeia cada parte (números → cards de stat, passos → timeline, riscos → callouts) e abre o `.html` no navegador.

---

## notes-tarefas

Recebe uma nota, tarefa ou lembrete no chat e a arquiva no repositório `~/notes`: classifica entre **task** (`tarefas/todo.md` ou `tarefas/rotina.md`), **conclusão** (`tarefas/hoje.md`) ou **ideia/nota** (pasta temática), normaliza a sintaxe (`due::` → `📅`, `#prio` → `⭐`), e comita e empurra. Quando a categoria (`#sol`/`#zas`/`#eu`) ou a pasta não estão claras, **pergunta em vez de chutar**.

Assume que `~/notes` existe — em cada máquina, como symlink para o clone real.

- `skills/notes-tarefas/SKILL.md` — o instruction file (formato das linhas, invariantes, workflow).

### Exemplo de uso

```
pagar fatura due:: 2026-07-12 #prio
```

```
italiano: sbloccare = desbloquear
```

---

## Instalação

### Claude Code — global (todos os projetos)

```bash
git clone https://github.com/d3m4/skills
```

Copie a pasta da skill para o diretório global de skills do Claude:

**Linux/macOS:**
```bash
cp -r skills/skills/htmlize ~/.claude/skills/htmlize
```

**Windows (PowerShell):**
```powershell
Copy-Item -Recurse skills\skills\htmlize "$env:USERPROFILE\.claude\skills\htmlize"
```

Use com `/htmlize` ou "htmlize esse arquivo".

### Claude Code — por projeto

Copie para a pasta `.claude/skills` do projeto:

```bash
cp -r skills/skills/htmlize .claude/skills/htmlize
```

### Codex / outros agentes

O `SKILL.md` é um instruction file portátil — não depende de runtime do Claude. Aponte o agente para ele:

- **Codex**: copie `skills/htmlize/SKILL.md` para o diretório de skills do Codex (ex.: `~/.agents/skills/htmlize/`) ou referencie no `AGENTS.md`.
- **Outros agentes**: cole o conteúdo do `SKILL.md` no prompt de sistema, ou referencie o arquivo no diretório de instruções equivalente do seu agente.

A "receita" (CDNs, tema, componentes, variações de comando por SO) está toda no `SKILL.md` — qualquer agente capaz de ler arquivos e rodar comandos consegue executá-la.

---

## Estrutura do repo

```
skills/
├── README.md
└── skills/
    ├── htmlize/
    │   ├── SKILL.md       # instruction file (receita do estilo htmlize)
    │   └── template.html  # esqueleto com CSS pronto + seções placeholder
    ├── discuta-comigo/
    │   └── SKILL.md       # instruction file (processo de descoberta em rodadas)
    └── notes-tarefas/
        └── SKILL.md       # instruction file (organização do repo ~/notes)
```
