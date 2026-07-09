---
name: notes-tarefas
description: Use quando o usuário envia uma nota/tarefa no Telegram ou terminal e você precisa organizá-la no sistema de tarefas do repositório ~/notes — decidindo se é task (todo.md/rotina.md) ou ideia/nota (pasta temática), perguntando a categoria se não souber. Também cobre marcar tarefa como concluída. Trigger: enviar nota, tarefa, lembrete ou anotação no chat.
---

# notes-tarefas — organizar notas e tarefas no repositório

## Trigger

Usuário envia uma mensagem no chat (Telegram ou terminal) com uma nota, lembrete, tarefa, anotação ou aviso de tarefa concluída, para ser organizada no repositório de notas.

## Onde fica o repositório

Sempre `~/notes`. Em toda máquina isso é um **symlink** para o clone real (ex.: `~/dev/gh/notes` no Linux, `C:\dev\github\notes` no Windows) — trate `~/notes` como o caminho canônico e nunca escreva o caminho do clone.

Se `~/notes` não existir, **pare e avise o usuário** para criar o symlink; não saia procurando o clone.

## Contexto do sistema

### Os 4 arquivos de tarefas

| Arquivo | O que é | Categoria obrigatória? |
|---------|---------|:----------:|
| **`tarefas/inbox.md`** | captura crua — o usuário joga sem pensar | ❌ |
| **`tarefas/rotina.md`** | recorrentes (nunca somem), agrupados por seção | ✅ |
| **`tarefas/todo.md`** | backlog de tarefas únicas (faz → some) | ✅ |
| **`tarefas/hoje.md`** | o dia — descartável, regenerado toda manhã | — |

### Você não está sozinho: o `scripts/notes-tasks.sh`

De hora em hora, um script roda no repositório e:

1. **Esvazia o `inbox.md`**: manda cada item para um LLM (`claude -p`) que decide `todo` ou `rotina` e **chuta a categoria sem perguntar a ninguém**.
2. **Remonta o `hoje.md`**: mescla toda a `rotina.md` + os `todo`s com `⏳` de hoje, sem apagar o que já está marcado.

Consequência prática: **o inbox não é um lugar seguro para um caso ambíguo.** Jogar lá é delegar o palpite a outro LLM. Se você está em dúvida, **pergunte** (ver regra fundamental).

### Categorias

- `#sol` — atividade/estudo/projetos pessoais
- `#zas` — trabalho (ZAS / Fatto / TFS)
- `#eu` — admin pessoal (contas, saúde, burocracia)

Subcategorias com barra são permitidas para projetos: `#sol/malauncher`, `#sol/mabrain`. A categoria-raiz (antes da barra) precisa ser uma das três acima — é dela que o script deriva a seção.

### Datas

- `📅 YYYY-MM-DD` — prazo ("tem que estar feito até")
- `⏳ YYYY-MM-DD` — alvo ("pretendo atacar nesse dia"); é o gancho que puxa a tarefa pro `hoje.md`
- Opcionais e **sempre absolutas** (ISO). Converta "amanhã"/"dia 12" antes de gravar.

### Prioridade

- `⭐` — prioritário, logo após o checkbox

### Você é o normalizador

O usuário digita `due:: 2026-07-10`, `sched:: 2026-07-05`, `#prio` ou `!` porque digitar emoji é chato. **O arquivo salvo só contém emoji.** Traduza sempre; nunca grave a forma textual.

| Usuário digita | Você grava |
|---|---|
| `due:: 2026-07-10` | `📅 2026-07-10` |
| `sched:: 2026-07-05` | `⏳ 2026-07-05` |
| `#prio` ou `!` | `⭐` |

### Formato de cada linha

```
- [ ] ⭐ Descrição da tarefa #categoria 📅 2026-07-12 ⏳ 2026-07-10
```

Ordem fixa: checkbox → `⭐` → descrição → `#categoria` → `📅` → `⏳`.

Subtarefas aninhadas com indentação:
```
- [ ] Tarefa principal #sol
  - [ ] Subtarefa 1
  - [ ] Subtarefa 2
```

### Formato das seções (`rotina.md` e `hoje.md`)

```markdown
## ☀️ sol #sol
## 💼 zas #zas
## 🙂 eu #eu
```

**A hashtag tem que ser o último token da linha.** O `notes-tasks.sh` casa o cabeçalho com `^## .*#<tag>$` e extrai a tag com `/#[a-z]+$/`. Uma seção `## 🏠 casa` (sem `#casa` no fim) fica invisível para o script para sempre.

## Invariantes que não se quebram

- **Todo arquivo em `tarefas/` tem `draft: true` no frontmatter.** É só isso que mantém a pasta fora do build público do Quartz — e tarefa pessoal (fatura, saúde) não pode virar site. Ao criar ou reescrever qualquer arquivo ali, preserve o frontmatter:
  ```markdown
  ---
  title: 🗄️ todo
  draft: true
  ---
  ```
- **Nunca marque `- [x]` em `rotina.md`** — é template, não backlog. A marcação acontece no `hoje.md`.
- **Nunca adicione tarefas novas ao `hoje.md`** — o script o remonta. (Marcar concluída lá é permitido; ver abaixo.)
- **Nunca edite `readme.md` de áreas existentes** sem instrução explícita — são visão/plano.
- **Datas sempre ISO** no texto salvo.
- Nomes de pastas/arquivos: **minúsculas, sem espaços nem acentos** (ascii-safe).

## Regra fundamental: classificar, e se não souber, PERGUNTAR

1. **Classifique** o tipo sozinho: é **task** (`todo.md`/`rotina.md`), **conclusão** (`hoje.md`) ou **ideia/nota** (pasta temática)?
2. **Se não souber a categoria** (`#sol`/`#zas`/`#eu`) de uma task, **pergunte** — nunca invente, nunca desovar no inbox para o script adivinhar.
3. **Se não souber a pasta temática** de uma ideia/nota, **pergunte** — nunca invente.
4. Se a mensagem já traz o contexto (`zas:`, `#sol`, `italiano:`, "joga no inbox"), use-o e não pergunte.

## Workflow

### 1. Interpretar a mensagem

| Tipo | Exemplo | Destino |
|------|---------|---------|
| **Task única** | "pagar fatura dia 12" / "terminar relatório" | `todo.md` |
| **Task recorrente** | "toda manhã: revisar Anki" / "daily: registrar atividade" | `rotina.md` |
| **Captura crua** | "joga no inbox: talvez um curso de blender" | `inbox.md` |
| **Concluída** | "já escovei os dentes" / "feito: pagar fatura" | `hoje.md` (+ `todo.md`) |
| **Nota de língua** | "italiano: sbloccare = desbloquear" | `lang/<idioma>/vocabulario.md` |
| **Log de prática** | "drawing: 20min sketch" / "writing: diário 15min" | `drawing/log.md` · `writing/log.md` |
| **Ideia de projeto** | "ideia: um CLI que traduz markdown" | `ideias/<projeto>/readme.md` |
| **Nota técnica** | "strudel dnb tem bug no sample rate" | `musica/strudel/anotacoes.md` |

O `inbox.md` só recebe algo quando o **usuário pedir explicitamente** ("joga no inbox", "captura isso", "depois eu vejo"). Ambiguidade sua não é motivo — pergunte.

### 2. Quando perguntar

- **Task sem categoria clara**: _"Essa task é `#sol`, `#zas` ou `#eu`?"_
- **Ideia/nota sem pasta clara**: _"Essa nota vai em qual pasta? (lang/, drawing/, writing/, ideias/, musica/, llms/, infra/, docs/, other/)"_
- **Ambíguo entre task e ideia**: _"É uma task pra fazer ou uma ideia pra registrar?"_

### 3. Inserir no arquivo correto

**`todo.md`** — append no final. Categoria inline, sempre. Datas só se mencionadas.
```
- [ ] ⭐ Pagar fatura #eu 📅 2026-07-10 ⏳ 2026-07-08
```

**`rotina.md`** — inserir dentro da seção `##` da categoria. **Sem categoria inline** (vem do cabeçalho).
```
- [ ] Revisar Anki
```
Se a seção não existir, crie no fim do arquivo no formato `## <emoji> <nome> #<tag>` — a hashtag no fim, ou o script ignora a seção.

**`inbox.md`** — append no final, depois do último item, sem categoria e sem data. Se houver um `- [ ]` vazio no fim, escreva **acima** dele.
```
- [ ] Curso de blender
```

**`hoje.md` (concluir tarefa)** — troque `- [ ]` por `- [x]` na linha correspondente. Se a tarefa é única e veio do `todo.md`, marque `- [x]` **também no `todo.md`**; senão o `⏳` de hoje a traz de volta amanhã. Se veio da `rotina.md`, marque só no `hoje.md`.

> Isso resolve, para o caminho manual, a questão em aberto registrada em `tarefas/regras.md` ("tarefa concluída no hoje.md não some do todo.md"). O script continua sem fazer essa propagação.

**Notas em pastas temáticas** — siga o padrão do arquivo existente: vocabulário vira linha da tabela/lista; log vira linha com data, tempo e descrição; nota técnica vira bullet ou parágrafo novo.

Pastas novas para ideias novas: `ideias/<nome-ascii-safe>/readme.md`.

### 4. Commit e push

```bash
cd ~/notes
git add -A
git commit -m "mensagem curta em pt-BR, imperativo, ~60 chars"
git push
```

Se o push falhar por divergência, `git pull --rebase` e tente de novo. Verifique o exit code do commit antes de dar por feito.

Há um `notes-sync.timer` que também comita de hora em hora — empurrar na hora evita que sua mudança fique parada esperando o timer.

## Estrutura do repo (para notas não-tarefa)

```
notes/
├── tarefas/{inbox,rotina,todo,hoje}.md
├── lang/{norsk,italiano,zhongwen,espanol}/{readme,vocabulario,gramatica,...}.md
├── drawing/{readme,log}.md
├── writing/{readme,log}.md
├── llms/{readme,local,ita2/...,pi/rpg/...}.md
├── musica/strudel/{readme,anotacoes,dnb-liquid,lofi-generativo}.md
├── ideias/{projeto}/{readme,...}.md
├── infra/{readme,miniserver/...}.md
├── docs/superpowers/specs/*.md
├── scripts/{notes-tasks.sh,sync-notes.sh,sync-notes.ps1}
├── rng/*.html
└── other/*.md
```

Convenções: cada pasta temática tem `readme.md` com visão/plano; callouts `> [!quote|tip|info|note|abstract|example|warning]`; wiki-links `[[caminho|texto]]`; links locais `[texto](arquivo.md)`.

## Pitfalls

- Escrever o caminho do clone em vez de `~/notes`.
- Criar seção em `rotina.md` sem a hashtag no fim do cabeçalho → o script nunca insere nada nela.
- Reescrever um arquivo de `tarefas/` e perder o `draft: true` → tarefa pessoal vai pro site público.
- Gravar `due::`/`#prio` no arquivo em vez do emoji.
- Usar o `inbox.md` como escape para a própria dúvida → o script vai chutar a categoria sozinho.
- Adicionar tarefa direto no `hoje.md` → o script a sobrescreve na próxima hora.
