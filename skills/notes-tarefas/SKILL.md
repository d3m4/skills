---
name: notes-tarefas
description: Use quando o usuário envia uma nota/tarefa no Telegram ou terminal e você precisa organizá-la no sistema de tarefas do repositório ~/notes — decidindo se é task (todo.md/rotina.md) ou ideia/nota (pasta temática), perguntando a categoria se não souber. Trigger: enviar nota no chat.
---

# notes-tarefas — organizar notas e tarefas no repositório

## Trigger

Usuário envia uma mensagem no chat (Telegram ou terminal) com uma nota, lembrete, tarefa, ou anotação para ser organizada no repositório de notas.

## Contexto do sistema

O repositório `~/notes` (symlink → `~/dev/gh/notes`) tem um sistema de tarefas em `tarefas/`:

### Os 4 arquivos de tarefas

| Arquivo | O que é | Categoria? |
|---------|---------|:----------:|
| **`tarefas/inbox.md`** | captura crua — jogar sem pensar | ❌ |
| **`tarefas/todo.md`** | backlog de tarefas únicas (faz → some) | ✅ |
| **`tarefas/rotina.md`** | recorrentes (nunca somem), por seção | ✅ |
| **`tarefas/hoje.md`** | o dia — descartável, regenerado toda manhã | — |

### Categorias

- `#sol` — atividade/estudo/projetos pessoais
- `#zas` — trabalho (ZAS / Fatto / TFS)
- `#eu` — admin pessoal (contas, saúde, burocracia)

### Datas

- `📅 YYYY-MM-DD` — prazo (input: `due:: YYYY-MM-DD`)
- `⏳ YYYY-MM-DD` — alvo / dia pretendido (input: `sched:: YYYY-MM-DD`)
- Datas são **opcionais** e **sempre absolutas** (ISO), nunca "hoje"/"amanhã"

### Prioridade

- `⭐` — prioritário (input: `#prio` ou `!`)

### Formato de cada linha

```
- [ ] Descrição da tarefa #categoria 📅 2026-07-12 ⏳ 2026-07-10
```

Subtarefas aninhadas com indentação:
```
- [ ] Tarefa principal #sol
  - [ ] Subtarefa 1
  - [ ] Subtarefa 2
```

### Estrutura geral do repo (para notas não-tarefa)

```
notes/
├── lang/{norsk,italiano,zhongwen,espanol}/{readme,vocabulario,gramatica,...}.md
├── drawing/{readme,log}.md
├── writing/{readme,log}.md
├── llms/{readme,local,ita2/...}.md
├── musica/strudel/{readme,anotacoes,dnb-liquid,lofi-generativo}.md
├── ideias/{projeto}/{readme,...}.md
├── docs/superpowers/specs/*.md
├── other/*.md
└── tarefas/{inbox,todo,rotina,hoje}.md
```

### Convenções gerais do repo

- Nomes de pastas/arquivos: **minúsculas, sem espaços nem acentos** (ascii-safe)
- Datas: formato absoluto ISO (`2026-07-09`), nunca "hoje"/"amanhã" no texto salvo
- Cada pasta de tema: `readme.md` com visão/plano
- Callouts opcionais: `> [!quote]`, `> [!tip]`, `> [!info]`, `> [!note]`, `> [!abstract]`, `> [!example]`, `> [!warning]`
- Wiki-links entre áreas: `[[caminho|texto]]`
- Links locais: `[texto](arquivo.md)`

## Regra fundamental: classificar, e se não souber, PERGUNTAR

1. **Classifique** o tipo sozinho: é **task** (vai pra `todo.md`/`rotina.md`) ou **ideia/nota** (vai pra pasta temática)
2. **Se não souber a categoria** (`#sol`/`#zas`/`#eu`) para uma task, **pergunte** — nunca invente
3. **Se não souber a pasta temática** para uma ideia/nota, **pergunte** — nunca invente
4. Se a mensagem vier com clarifier explícito (`zas:`, `#sol`, `italiano:`, etc.), use esse contexto — aí não pergunte

## Workflow

### 1. Interpretar a mensagem do usuário

A mensagem pode ser de vários tipos:

| Tipo | Exemplo | Destino |
|------|---------|---------|
| **Task única** | "pagar fatura dia 12" / "terminar relatório" / "comprar presente" | `todo.md` |
| **Task recorrente** | "toda manhã: revisar Anki" / "daily: registrar atividade" | `rotina.md` |
| **Captura crua** | "ah, e talvez fazer um curso de blender" (sem compromisso) | `inbox.md` |
| **Nota de língua** | "italiano: sbloccare = desbloquear" / "norsk: å glede seg til" | `lang/<idioma>/vocabulario.md` |
| **Log de prática** | "drawing: 20min sketch hoje" / "writing: diário 15min" | `drawing/log.md` ou `writing/log.md` |
| **Ideia de projeto** | "ideia: um CLI que traduz markdown automaticamente" | `ideias/<projeto>/readme.md` |
| **Nota técnica** | "strudel dnb tem bug no sample rate" | `musica/strudel/anotacoes.md` |

### 2. Quando perguntar

- **Task sem categoria clara**: _"Essa task é `#sol`, `#zas` ou `#eu`?"_
- **Ideia/nota sem pasta clara**: _"Essa nota vai em qual pasta? (lang/, drawing/, ideias/, musica/, llms/, docs/, other/)"_
- **Ambíguo entre task e ideia**: _"É uma task pra fazer ou uma ideia pra registrar?"_

Não pergunte quando a própria mensagem já deixa claro (ex: começa com "zas:" ou "italiano:").

### 3. Inserir no arquivo correto

#### Para `todo.md`:
- Append no final do arquivo (antes de linhas em branco finais, se houver)
- Formato: `- [ ] Descrição #categoria 📅 YYYY-MM-DD ⏳ YYYY-MM-DD`
- Sempre incluir a categoria inline
- Se mencionar prioridade, usar `- [ ] ⭐ Descrição #categoria`
- Datas só se explicitamente mencionadas

#### Para `rotina.md`:
- Inserir dentro da seção `##` correspondente à categoria
- Formato: `- [ ] Descrição` (sem categoria inline — a categoria vem do cabeçalho da seção)
- Se a seção não existir, criar no final antes do EOF

#### Para `inbox.md`:
- Append no final, antes da checklist vazia `- [ ]` se existir
- Formato: `- [ ] Descrição` (sem categoria, sem data)

#### Para notas em pastas temáticas:
- Seguir o padrão de conteúdo do arquivo existente
- Se for vocabulário: adicionar linha na tabela ou lista
- Se for log: adicionar linha na tabela com data, tempo, descrição
- Se for nota técnica: adicionar como novo parágrafo ou bullet point

### 4. Fazer commit e push

```bash
cd ~/notes
git add -A
git commit -m "mensagem curta em pt-BR, imperativo, ~60 chars"
git push
```

### Verificação final

- Commit feito com sucesso (verificar exit code)
- Se push falhar (rebase necessário), fazer `git pull --rebase` e tentar push de novo

## Pitfalls / Notas

- **Nunca modificar `hoje.md`** — ele é descartável e regenerado toda manhã pelo script `notes-tasks.sh`
- **Nunca editar `readme.md` de áreas existentes** a menos que explicitamente instruído — são visão/plano
- **Datas sempre ISO** no formato salvo — converter "amanhã"/"dia 12" para data absoluta
- **Criar pastas novas para ideias novas** seguindo o padrão `ideias/<nome-ascii-safe>/readme.md`
- Se a mensagem for ambígua, priorizar colocar em `inbox.md` (lugar seguro, depois processa)
- Após inserir, sempre fazer `git push` — o sync automático de hora em hora pode demorar
