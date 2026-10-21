---
name: design-excalidraw-frontend-flow
description: Cria ou evolui diagramas .excalidraw para análise funcional de frontends a partir de runbooks, documentação, DTOs, OpenAPI e código de APIs. Use quando for necessário representar uma jornada centrada nos retornos ao usuário, separar ações da interface de processos internos, desenhar páginas e formulários sem modal com campos reais, propor telas de listagem, identificar gaps de contrato/UX/segurança ou preservar ajustes manuais de um canvas Excalidraw existente. Também serve para converter um canvas com setas e rótulos soltos em canvas ligado. Gera setas como conectores ligados e rótulos vinculados às figuras, valida o JSON por script e confere o resultado renderizado em PNG.
---

# Design Excalidraw Frontend Flow

Produzir um canvas editável que conecte fluxo funcional, wireframes estruturais e gaps necessários para implementar o frontend.

`<skill>` abaixo é a pasta desta skill (onde está este SKILL.md).

## Executar o workflow

1. Localizar e ler o runbook, os contratos da API e as instruções do repositório.
2. Identificar entidades administráveis, estados, permissões, endpoints, campos de entrada, respostas e erros.
3. Se houver um `.excalidraw` fornecido pelo usuário, usá-lo como base. Comparar posições e dimensões com versões anteriores quando disponíveis.
4. Ler antes de desenhar:
   - [references/diagram-guidelines.md](references/diagram-guidelines.md): o que o canvas precisa conter;
   - [references/color-palette.md](references/color-palette.md): única fonte de cores, tamanhos de fonte e traços;
   - [references/element-templates.md](references/element-templates.md): JSON completo de cada elemento e como medir texto.
5. Usar [assets/frontend-runbook-example.excalidraw](assets/frontend-runbook-example.excalidraw) como referência concreta de composição, espaçamento, wireframes e ligações. Ele passa no validador sem erros nem avisos.
6. Planejar o layout por áreas (legenda, fluxo, páginas/formulários, listagens, gaps) e construir uma área por vez, conforme "Construir por áreas".
7. Rodar o loop de "Validar e renderizar" até passar.
8. Conferir o "Checklist de entrega" e informar o caminho absoluto do arquivo.

## Investigar antes de desenhar

- Tratar o runbook como descrição da jornada, não como única fonte de verdade.
- Cruzar nomes e obrigatoriedade dos campos com DTOs, schemas e validações reais.
- Cruzar estados e transições com serviços e endpoints.
- Registrar divergências entre runbook, OpenAPI, DTO e implementação; nunca escolher silenciosamente uma versão.
- Identificar permissões de leitura e escrita e os retornos `400`, `401`, `403`, `404`, `409` e `500` aplicáveis.
- Distinguir persistência, validação, ativação e aplicação efetiva de uma configuração.

Se uma informação essencial não puder ser descoberta e mudar materialmente o desenho, perguntar ao usuário. Caso contrário, avançar com uma hipótese explicitamente marcada como gap.

## Modelar o fluxo

- Iniciar em um bloco verde.
- Usar borda sólida para ação ou retorno percebido pelo usuário.
- Usar borda tracejada para processamento interno.
- Usar losangos para decisões e rotular as saídas.
- Mostrar internals somente quando produzirem retorno, erro, mudança de estado, espera ou próximo passo relevante.
- Manter setas, rótulos e nós sem sobreposição. Criar espaço vertical antes de alongar conectores através de outros elementos.
- Diferenciar sucesso, erro e estado neutro por cor sem depender apenas da cor para transmitir significado.
- Seta com rótulo (`Sim`/`Não`) precisa de no mínimo 60px; texto de losango usa `fontSize: 14` e no máximo duas linhas curtas.
- Com mais de uma jornada (ex.: consulta, importação CSV, wizard, edição), desenhar uma trilha por jornada, em colunas ou faixas com título, e ligar as trilhas só nos pontos de entrada e saída. Seta que atravessa o canvas inteiro de uma trilha a outra vira um nó de referência ("→ Trilha C") em vez de um conector longo.
- Nó do fluxo que abre uma página leva o código dela (`P1`, `P2`…), o mesmo que aparece no título do wireframe. Nó que depende de algo que a API não tem leva um marcador `GAP-n` com o id do gap correspondente na área de gaps.
- Quando houver processamento assíncrono, separar o status de negócio (ex.: configuração `ATIVA`/`INATIVA`) do status de processamento (ex.: `PENDENTE`/`PROCESSANDO`/`APLICADA`/`APLICADA_COM_ERRO`). Mostrar os dois no fluxo e nas telas, nunca um só status misturando os dois.

## Ligar os elementos

O diagrama precisa continuar editável à mão. Toda seta deve ser um conector ligado nas duas pontas e todo rótulo de nó deve ser texto vinculado ao seu container, de modo que arrastar uma figura leve junto as setas que chegam e saem dela e o texto que está dentro dela. Seta solta e texto posicionado por cima de uma figura não são aceitáveis.

Seta ligada recebe as duas pontas:

```json
"startBinding": { "elementId": "<id da figura de origem>", "focus": 0, "gap": 4 },
"endBinding":   { "elementId": "<id da figura de destino>", "focus": 0, "gap": 4 }
```

E as duas figuras precisam listar a seta:

```json
"boundElements": [ { "type": "arrow", "id": "<id da seta>" } ]
```

Rótulo dentro de um retângulo ou losango é um elemento de texto com `"containerId": "<id da figura>"` e `"verticalAlign": "middle"`, e a figura lista esse texto:

```json
"boundElements": [ { "type": "text", "id": "<id do texto>" } ]
```

Rótulo de nó e botão usam `"textAlign": "center"`. Placeholder de input usa `"textAlign": "left"` e continua vinculado ao campo.

Rótulo de seta, como o `Sim` e o `Não` de uma decisão, usa o mesmo mecanismo: o `containerId` do texto aponta para o id da seta e a seta lista o texto em `boundElements`.

O `boundElements` é bidirecional. Se a figura não listar a seta ou o texto, o vínculo não funciona, mesmo com o `startBinding`, o `endBinding` ou o `containerId` preenchidos. Uma figura que tem seta de entrada, seta de saída e rótulo lista as três entradas no mesmo `boundElements`.

Texto solto continua legítimo apenas para o que não pertence a figura nenhuma: título do canvas, legenda, notas de rodapé, cabeçalhos de seção, rótulos de campo acima do input e conteúdo de páginas e tabelas. Rótulo de nó e rótulo de seta, nunca.

## Construir por áreas

Um canvas completo passa facilmente de 400 elementos, e gerar tudo em uma resposta estoura o limite de saída e produz JSON truncado. Mesmo quando cabe, o resultado sai pior.

1. Criar o arquivo com o envelope (`type`, `version`, `source`, `appState`, `files`), o título, o escopo e a legenda.
2. Acrescentar **uma área por edição**, na ordem fluxo → páginas/formulários → listagens → gaps. Dedicar a cada área uma passada própria: layout, espaçamento e ligações.
3. Usar `id` descritivo com prefixo da área (`fluxo_`, `pag_rota_`, `lst_rotas_`, `gap_`) e `seed` numerado por área (fluxo 2xxxxx, páginas 3xxxxx…), como em [element-templates.md](references/element-templates.md).
4. Quando uma seta cruzar áreas, atualizar na mesma edição o `boundElements` da figura que já existia.
5. Rodar o validador ao fim de cada área. Erro de vínculo se corrige antes de começar a próxima.

Escrever o JSON à mão. Não criar script gerador de coordenadas, que esconde os erros, nem delegar a geração a um subagente, que não tem as regras desta skill.

## Validar e renderizar (obrigatório)

Não dá para julgar um diagrama pelo JSON. Depois de criar ou editar o canvas, rodar o loop abaixo até passar, normalmente em 2 a 4 voltas.

**1. Validar.**

```bash
python <skill>/scripts/validate_excalidraw.py <arquivo.excalidraw>
```

- `ERRO` são vínculos quebrados, ids duplicados ou estrutura inválida. A entrega não sai com erro. `--fix` acrescenta sozinho as referências de volta que faltam em `boundElements` e remove as órfãs, mas não cria vínculo novo.
- `AVISO` aponta texto que não cabe no container, sobreposição de figuras, seta atravessando figura, ponta de seta longe da figura e rótulo solto que devia estar vinculado. Cada aviso se corrige ou se justifica.

**2. Renderizar e olhar.**

```bash
python <skill>/scripts/render_excalidraw.py <arquivo.excalidraw> --out <tmp>/canvas.png
python <skill>/scripts/render_excalidraw.py <arquivo.excalidraw> --out <tmp>/area.png --crop X Y L A
python <skill>/scripts/render_excalidraw.py <arquivo.excalidraw> --out <tmp>/t.png --tiles 1600x1200
```

Abrir os PNGs com a ferramenta de leitura de imagem. A imagem inteira serve para julgar a composição. `--crop`, em coordenadas da cena, e `--tiles` servem para ler os textos e conferir as setas, porque um canvas grande inteiro vira miniatura. Salvar os PNGs em pasta temporária, não junto do entregável, a menos que o usuário peça.

**3. Conferir contra o plano:** a estrutura bate com o que foi planejado? O olho percorre o fluxo na ordem certa? Sucesso, erro e processamento interno são distinguíveis? Os wireframes mostram campos reais?

**4. Procurar defeitos:** texto cortado ou vazando, elementos sobrepostos, seta cruzando nó, seta chegando no lugar errado, rótulo ambíguo, espaçamento irregular, área apertada ao lado de área vazia, texto pequeno demais para ler.

**5. Corrigir e repetir** a partir do passo 1. Não parar na primeira volta sem defeitos graves se a composição ainda pode melhorar.

Requisitos do render: `python -m pip install --user playwright`. O script usa o Edge ou o Chrome instalados (`python -m playwright install chromium` só é necessário se nenhum dos dois existir) e carrega o Excalidraw do esm.sh, então precisa de internet. Sem render disponível, entregar com o validador limpo e avisar o usuário que a conferência visual não foi feita.

## Converter um canvas legado

Canvas antigo, com setas soltas e textos posicionados por cima das figuras, se converte sem mover as figuras:

```bash
python <skill>/scripts/bind_loose.py <entrada.excalidraw> --out <saida.excalidraw>
```

O script liga as pontas de seta à figura mais próxima (até 20px) e vincula o texto que é o único conteúdo de uma figura, mantendo o alinhamento original. Também vincula rótulos curtos perto do meio de uma seta. Molduras de página e cards com vários elementos ficam como estão. Depois de rodar, fazer o loop de validar e renderizar. Os avisos de texto que não cabe costumam aparecer em losangos.

## Desenhar o frontend

- Representar páginas completas e nunca modais.
- **Wireframe é desenho, não descrição.** Input, select, botão, radio, checkbox, card, tabela e stepper são figuras com texto vinculado. Um bloco de texto que escreve a tela ("[ Salvar ]", "( ) Todos (•) Por filtro", caixa ASCII) não é protótipo, e o validador avisa quando encontra isso. Uma descrição textual da página pode existir como nota ao lado, nunca no lugar do wireframe.
- Usar elementos HTML clássicos sem acoplar o desenho a uma biblioteca React. O vocabulário de componentes está em [element-templates.md](references/element-templates.md): cabeçalho do sistema, breadcrumb, stepper, card de resumo, radio, área de upload, tabela com seleção, paginação, aviso/callout e rodapé de ações.
- Para resumo de configurações ou entidades, preferir cards (nome, badges de status, contagens, ação "Ver") a tabela. Tabela fica para listas de seleção e histórico.
- Fluxo de criação em várias etapas vira wizard: uma página por passo, com stepper no topo, `Voltar`/`Avançar` no rodapé e uma página final de revisão com `Editar` por seção.
- Se a jornada pede uma entidade que a API não tem (ex.: um "bloco de configuração" que no back-end é só `Envio → Rotina → Itens`), propor o modelo mental da interface, desenhar a tela em cima dele e registrar a entidade como pendência do back-end. Nunca desenhar como se o contrato já existisse. Quando o fluxo inteiro for proposta, sem contrato, dizer isso no título ("proposta ideal").
- Incluir breadcrumb, título, campos reais, ajuda contextual e ações de página.
- Marcar obrigatórios e representar campos condicionais e coleções repetíveis.
- Criar páginas de confirmação para mudanças de estado ou ações destrutivas.
- Criar listagens para cada entidade administrável com busca, filtros, status, colunas úteis e ações por linha.
- Representar carregamento, vazio, nenhum resultado, falha, `401` e `403`.
- Não inventar paginação ou filtros server-side. Se o endpoint só retorna lista completa, marcar filtro local como alternativa de MVP e contrato paginado como gap de escala.
- Nunca levar `client_secret` ao navegador; modelar autenticação frontend com login corporativo/OIDC e autorização por perfil.

## Editar um canvas existente

1. Preservar IDs e elementos existentes sempre que possível.
2. Preservar coordenadas, tamanhos e conectores ajustados manualmente.
3. Acrescentar conteúdo em uma região livre do canvas.
4. Evitar regenerar a cena inteira.
5. Se o canvas tiver setas ou rótulos soltos, perguntar antes de converter com `bind_loose.py`, porque a conversão reescreve o arquivo inteiro.
6. Rodar o loop de validar e renderizar. Os vínculos precisam continuar consistentes conforme "Ligar os elementos".

## Checklist de entrega

- [ ] Fontes cruzadas (runbook × DTO × OpenAPI × código) e divergências registradas como gap.
- [ ] Áreas presentes: título/escopo/legenda, fluxo, páginas, listagens, gaps.
- [ ] Fluxo começa em bloco verde; sólido = usuário, tracejado = interno; decisões com saídas rotuladas.
- [ ] Páginas sem modal, desenhadas como figuras (nenhum aviso de protótipo textual), com campos e exemplos reais, obrigatórios marcados e confirmação para ação destrutiva.
- [ ] Códigos `P1…Pn` batem entre nós do fluxo e títulos das páginas; marcadores `GAP-n` existem na área de gaps.
- [ ] Listagens com busca, filtros, status, ações por linha e estados (carregando, vazio, sem resultado, falha, 401, 403).
- [ ] Cores e tamanhos só da paleta.
- [ ] `validate_excalidraw.py` sem `ERRO`, com cada `AVISO` corrigido ou justificado.
- [ ] Render conferido (inteiro + recortes) sem texto vazando, sobreposição ou seta cruzando nó.
- [ ] Caminho absoluto informado.

## Entregar

- Salvar um `.excalidraw` válido e editável.
- Salvar junto um `.md` com a análise: fontes lidas, endpoints e contratos reais, decisões tomadas com o usuário, gaps por prioridade e o caminho do canvas. É o que preserva o raciocínio quando o canvas for refeito. Se o usuário já tem um documento de análise, atualizar esse em vez de criar outro.
- Informar sempre o caminho absoluto completo, de cada arquivo.
- Resumir áreas adicionadas e gaps relevantes, e dizer se o render foi conferido.
- Não alterar contratos ou código de produção durante uma tarefa apenas de análise, salvo solicitação explícita.
