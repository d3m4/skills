# Templates de elementos

Elementos completos para copiar. Cores vêm de [color-palette.md](color-palette.md). Todo exemplo abaixo já segue a regra de ligação do SKILL.md: o que está dentro de uma figura é texto vinculado, e toda seta é ligada nas duas pontas.

## Documento

```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "https://excalidraw.com",
  "elements": [],
  "appState": { "viewBackgroundColor": "#ffffff", "gridSize": 20 },
  "files": {}
}
```

## Campos comuns

Todo elemento leva estes campos. Os templates abaixo mostram só o que muda.

```json
{
  "id": "fluxo_valida_rota",
  "type": "rectangle",
  "x": 0, "y": 0, "width": 230, "height": 80,
  "angle": 0,
  "strokeColor": "#1e1e1e", "backgroundColor": "#dbe4ff",
  "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
  "roughness": 1, "opacity": 100,
  "groupIds": [], "frameId": null,
  "roundness": { "type": 3 },
  "seed": 210001, "version": 1, "versionNonce": 210001,
  "isDeleted": false, "boundElements": [],
  "updated": 1, "link": null, "locked": false
}
```

- `id` descritivo, com prefixo da área: `legenda_`, `fluxo_`, `pag_<pagina>_`, `lst_<entidade>_`, `gap_`. Isso deixa legível a referência entre áreas.
- `seed` e `versionNonce` são numerados por área para não colidir: legenda 1xxxxx, fluxo 2xxxxx, páginas 3xxxxx, listagens 4xxxxx, gaps 5xxxxx.

## Medir texto

O Excalidraw não recalcula sozinho a caixa do texto ao abrir o arquivo. Calcule:

- largura ≈ maior linha × `fontSize` × 0,52 (minúsculas) ou 0,64 (maiúsculas e dígitos), na `fontFamily: 5`;
- altura = número de linhas × `fontSize` × 1,25.

A área útil do container, já descontado o padding de 5px de cada lado, é:

| Container | Largura útil | Altura útil |
|---|---|---|
| `rectangle` | `width − 10` | `height − 10` |
| `diamond` | `width / 2 − 10` | `height / 2 − 10` |
| `ellipse` | `width × 0,707 − 10` | `height × 0,707 − 10` |

Se o texto não cabe, quebre a linha com `\n` ou alargue a figura. O losango é o caso mais comum: 170×90 com `fontSize: 14` comporta duas linhas de até cerca de 10 caracteres ("Perfil de\ngestão?").

## Nó com rótulo (retângulo, tracejado ou losango)

Figura:

```json
{ "id": "fluxo_valida_rota", "type": "rectangle",
  "x": 1110, "y": 460, "width": 230, "height": 80,
  "strokeStyle": "dashed", "backgroundColor": "transparent",
  "boundElements": [
    { "type": "text",  "id": "fluxo_valida_rota_txt" },
    { "type": "arrow", "id": "fluxo_seta_solicita_valida" },
    { "type": "arrow", "id": "fluxo_seta_valida_decisao" }
  ] }
```

Texto vinculado, centralizado no container (`x = centro − largura/2`, `y = centro − altura/2`):

```json
{ "id": "fluxo_valida_rota_txt", "type": "text",
  "x": 1135.6, "y": 478.75, "width": 178.8, "height": 42.5,
  "strokeColor": "#1e1e1e", "backgroundColor": "transparent",
  "roundness": null, "boundElements": null,
  "text": "Compila configuração\nsem aplicar", "originalText": "Compila configuração\nsem aplicar",
  "fontSize": 17, "fontFamily": 5, "lineHeight": 1.25,
  "textAlign": "center", "verticalAlign": "middle",
  "containerId": "fluxo_valida_rota", "autoResize": true }
```

Losango: `"type": "diamond"`, `"roundness": null`, `backgroundColor: "#fff3bf"`, `fontSize: 14` no texto.

## Seta ligada com rótulo

`x`/`y` da seta é a ponta de origem, e `points` é relativo a ela. A ponta fica a `gap` px da borda da figura.

```json
{ "id": "fluxo_seta_decisao_nao", "type": "arrow",
  "x": 545, "y": 590, "width": 45, "height": 0,
  "backgroundColor": "transparent", "roundness": { "type": 2 },
  "points": [[0, 0], [-45, 0]],
  "startBinding": { "elementId": "fluxo_decisao_rota_valida", "focus": 0, "gap": 4 },
  "endBinding":   { "elementId": "fluxo_erro_rota",           "focus": 0, "gap": 4 },
  "startArrowhead": null, "endArrowhead": "arrow",
  "elbowed": false, "lastCommittedPoint": null,
  "boundElements": [ { "type": "text", "id": "fluxo_seta_decisao_nao_txt" } ] }
```

Rótulo da seta, centralizado no ponto médio do comprimento da seta:

```json
{ "id": "fluxo_seta_decisao_nao_txt", "type": "text",
  "x": 511.6, "y": 581.9, "width": 21.8, "height": 16.25,
  "text": "Não", "originalText": "Não", "fontSize": 13, "fontFamily": 5, "lineHeight": 1.25,
  "textAlign": "center", "verticalAlign": "middle",
  "containerId": "fluxo_seta_decisao_nao", "autoResize": true,
  "roundness": null, "boundElements": null }
```

Seta com rótulo precisa de no mínimo 60px de comprimento, senão o rótulo encosta na ponta.

Para desviar de uma figura, acrescente pontos intermediários: `"points": [[0,0],[0,-60],[300,-60],[300,0]]`. Não atravesse nós.

## Wireframes

**Input com placeholder.** O texto fica vinculado ao campo, alinhado à esquerda, e o rótulo do campo fica solto acima dele.

```json
{ "id": "pag_rota_chave_lbl", "type": "text", "x": 810, "y": 1840, "text": "Chave da rota *",
  "fontSize": 12, "strokeColor": "#1e1e1e", "textAlign": "left", "verticalAlign": "top", "containerId": null }
{ "id": "pag_rota_chave", "type": "rectangle", "x": 810, "y": 1862, "width": 400, "height": 34,
  "strokeWidth": 1, "backgroundColor": "#ffffff",
  "boundElements": [ { "type": "text", "id": "pag_rota_chave_ph" } ] }
{ "id": "pag_rota_chave_ph", "type": "text", "x": 818, "y": 1871.5, "text": "CONSULTAR-BENEFICIARIO",
  "fontSize": 12, "strokeColor": "#868e96", "textAlign": "left", "verticalAlign": "middle",
  "containerId": "pag_rota_chave" }
```

**Botão:** retângulo de 110×36 com texto centralizado vinculado e as cores de botão primário ou secundário.

**Select:** igual ao input, com placeholder `"Todas ▾"`.

**Checkbox:** quadrado de 18×18, `strokeWidth: 1`, com o texto solto à direita. É texto solto porque o rótulo fica fora da figura.

**Página:** moldura `#f8f9fa`. Título, breadcrumb, rótulos de campo e notas são texto solto dentro dela. Uma moldura nunca recebe rótulo vinculado, porque contém muitas coisas.

**Tabela:** um retângulo de cabeçalho (`#e7f5ff`) e um retângulo por linha. As células são texto solto. Badges e botões de ação por linha são figuras com texto vinculado.
