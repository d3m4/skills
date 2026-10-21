# Orientação para criação de diagrama Excalidraw

Use esta orientação como template para produzir diagramas de análise funcional e levantamento de necessidades de frontend a partir de runbooks, documentação e contratos reais de uma API.

## Objetivo

Criar um arquivo `.excalidraw` editável contendo:

1. O fluxo funcional descrito pelo runbook.
2. Somente os processamentos internos que produzam algum resultado, mudança de estado ou retorno relevante para o usuário.
3. As páginas e formulários necessários para implementar um frontend.
4. As telas de listagem e consulta que dão acesso às jornadas.
5. Uma seção separada com gaps, inconsistências e necessidades identificadas.

O frontend ainda não precisa existir. Represente componentes estruturais clássicos de HTML, sem assumir uma biblioteca específica de React.

## Referência visual

- O fluxo deve começar em um bloco verde.
- Blocos com borda sólida representam ações realizadas pelo usuário ou respostas apresentadas pela interface.
- Blocos com borda tracejada representam processamento interno do sistema.
- Blocos verdes representam sucesso, confirmação ou conclusão positiva.
- Blocos vermelhos representam erro, impedimento ou retorno negativo.
- Losangos representam decisões.
- Setas devem mostrar claramente a sequência e conter rótulos como `Sim` e `Não` quando saírem de uma decisão.
- Setas devem ser conectores ligados às figuras de origem e destino, e rótulos de nó e de seta devem ser textos vinculados aos seus containers.
- Inclua uma legenda no início do canvas.
- Use somente as cores e os tamanhos de [color-palette.md](color-palette.md).

## Recorte do fluxo

- Comece pela ação que inicia a jornada do usuário.
- Não detalhe todas as classes, serviços, repositórios ou integrações internas.
- Mostre um processamento interno apenas quando ele:
  - validar dados;
  - alterar um estado percebido pelo usuário;
  - produzir sucesso ou erro;
  - influenciar o próximo passo da jornada;
  - exigir espera, atualização ou nova tentativa;
  - gerar dados que serão exibidos na interface.
- Diferencie claramente dados apenas persistidos daqueles efetivamente carregados ou aplicados pelo sistema.
- Represente caminhos alternativos e retornos de erro importantes.

## Organização do canvas

Organize o conteúdo em áreas visualmente separadas, preferencialmente nesta ordem:

1. Título, escopo e legenda.
2. Fluxo principal do runbook.
3. Páginas e formulários.
4. Telas de listagem.
5. Gaps e necessidades.

Deixe espaço suficiente entre linhas do fluxo para losangos, rótulos e setas. Evite qualquer sobreposição entre nós, textos e conectores. Quando uma seta precisar atravessar uma linha do fluxo, aumente seu comprimento e reposicione os elementos para manter a leitura clara.

Os elementos precisam estar ligados entre si, e não apenas posicionados lado a lado. Cada seta deve ter `startBinding` e `endBinding` apontando para as figuras que conecta, e cada figura deve listar essa seta em `boundElements`. Cada rótulo de nó deve ser um texto com `containerId` apontando para a figura, e a figura deve listar esse texto em `boundElements`. Rótulos de seta, como `Sim` e `Não`, seguem a mesma regra, com o `containerId` apontando para a seta. Como o `boundElements` é bidirecional, o vínculo só funciona quando os dois lados se referenciam. Assim, arrastar uma figura leva junto suas setas e seu texto, e o canvas continua editável à mão. Texto solto fica reservado ao que não pertence a figura nenhuma, como título, legenda, cabeçalhos de seção e notas de rodapé. O arquivo de exemplo da skill segue essa regra e serve de referência para ligações, composição, espaçamento e wireframes.

## Páginas e formulários

- Desenhe páginas completas, não modais, com os controles desenhados como figuras. Texto descrevendo a tela (`[ Salvar ]`, `( ) opção`) não substitui o wireframe.
- Use breadcrumb, título da página, campos, textos de ajuda e ações no rodapé.
- Use os nomes reais dos campos dos DTOs ou contratos da API.
- Marque campos obrigatórios com `*`.
- Use controles semanticamente adequados:
  - texto e URL: `input`;
  - valores enumerados: `select`;
  - booleanos: `checkbox` ou `switch`;
  - textos longos: `textarea`;
  - coleções: seções repetíveis dentro da página.
- Mostre exemplos realistas dentro dos campos.
- Indique dependências entre campos, como campos habilitados somente quando determinado booleano estiver ativo.
- Para coleções aninhadas, represente visualmente como adicionar, editar e remover itens sem modal.
- Inclua ações como `Cancelar`, `Salvar`, `Validar` e outras ações reais da jornada.
- Se uma operação mudar estado ou for destrutiva, use uma página de confirmação, não modal.

## Telas de listagem

Para cada entidade administrável, desenhe uma página de listagem contendo:

- breadcrumb e título;
- ação primária para criar um registro, quando autorizada;
- busca textual;
- filtros relevantes;
- quantidade de resultados;
- tabela com as colunas mais úteis para decisão do usuário;
- badges de situação, como `Ativo` e `Inativo`;
- ações por linha, como detalhar, editar, validar, testar, ativar ou desativar;
- paginação somente quando suportada ou identificada explicitamente como necessidade futura.

Considere também os seguintes estados:

- carregamento;
- lista vazia;
- nenhum resultado para os filtros;
- erro de carregamento;
- sessão expirada (`401`);
- acesso negado (`403`).

Quando o backend retornar a lista completa e não aceitar paginação ou filtros, deixe explícito que:

- busca e filtros podem ser locais no MVP se o volume for pequeno;
- parâmetros não suportados não devem ser enviados à API;
- paginação, ordenação e filtros server-side são gaps de contrato para cenários de maior volume.

## Segurança e permissões

- Não represente `client_secret` ou fluxo `client_credentials` como algo executado diretamente pelo navegador.
- Para frontend, considere autenticação corporativa por OIDC e token/sessão de usuário.
- Identifique as permissões necessárias para consulta e gestão.
- Ações não autorizadas devem ser ocultadas ou desabilitadas conforme o padrão da empresa.
- Represente os retornos `401` e `403` na análise de estados da interface.

## Feedback e tratamento de erros

- Mostre confirmações após operações bem-sucedidas.
- Mostre erros de campo próximos dos respectivos controles.
- Diferencie validação local da validação retornada pelo backend.
- Considere os retornos `400`, `401`, `403`, `404`, `409` e `500` quando aplicáveis.
- Em falhas técnicas, apresente o `X-Correlation-Id` para suporte e rastreabilidade.
- Preserve mensagens de negócio úteis retornadas pela API.
- Não exponha dados sensíveis, tokens ou segredos no diagrama ou na interface proposta.

## Análise de gaps

Crie uma área separada no canvas para registrar, no mínimo:

- contratos ausentes ou incompletos;
- inconsistências entre runbook, DTO, OpenAPI e implementação;
- autenticação e autorização necessárias;
- campos condicionais e validações;
- estados que precisam ser comunicados ao usuário;
- listagens ou páginas necessárias que não estejam descritas no runbook;
- ausência de paginação, busca, filtros ou ordenação no backend;
- decisões de produto ainda abertas;
- diferenças entre persistir uma configuração e aplicá-la efetivamente;
- ações operacionais que talvez devam ficar restritas a usuários avançados.

Não corrija silenciosamente uma contradição encontrada. Registre-a como gap e indique quais fontes discordam.

Organize os gaps por prioridade e numere cada um (`GAP-1`, `GAP-2`…), para que os marcadores no fluxo apontem para eles:

- `P0`: bloqueia o frontend (entidade ou endpoint inexistente, segurança);
- `P1`: contrato incompleto ou divergente entre fontes;
- `P2`: melhoria de escala, UX ou operação.

Mantenha as decisões de produto em aberto num quadro próprio, separado dos gaps técnicos. Quando houver muitas pendências, feche a área com uma linha de estratégia por fases (ex.: "Fase 1: modelo e listagem · Fase 2: edição · Fase 3: CSV").

## Rastreabilidade entre áreas

- Cada página recebe um código (`P1`, `P2`…) no título do wireframe, e o nó do fluxo que leva a ela mostra o mesmo código.
- Um nó do fluxo que depende de algo ausente na API recebe um marcador `GAP-n` apontando para o gap correspondente.
- O `.md` de análise entregue junto com o canvas usa os mesmos códigos.

## Preservação de versões editadas

Quando receber uma versão do `.excalidraw` alterada manualmente pelo usuário:

1. Use essa versão como nova base.
2. Compare posições, dimensões e conectores com a versão anterior.
3. Preserve todos os ajustes manuais de legibilidade.
4. Acrescente novos elementos em uma área livre do canvas.
5. Não regenere o diagrama inteiro se isso puder desfazer ajustes do usuário.
6. Valide o JSON final com `scripts/validate_excalidraw.py`, que confere `id` e `type` de todos os elementos, que toda seta tem `startBinding` e `endBinding`, que todo id referenciado existe e que cada figura ou seta lista de volta em `boundElements` o que aponta para ela. Depois, confira o render com `scripts/render_excalidraw.py`.

## Entrega esperada

- Um arquivo `.excalidraw` válido e editável.
- O arquivo deve ficar em uma localização claramente informada.
- Ao concluir, forneça o caminho absoluto completo.
- Informe resumidamente as áreas adicionadas e os principais gaps encontrados.

## Exemplo de solicitação curta

> Analise o runbook e os contratos reais da API. Crie um diagrama Excalidraw seguindo o arquivo `ORIENTACAO-TEMPLATE-EXCALIDRAW.md`. Mostre o fluxo centrado nos retornos ao usuário, desenhe páginas puras sem modal, inclua formulários com campos reais, telas de listagem e uma área separada de gaps. Preserve qualquer ajuste manual existente no arquivo base.
