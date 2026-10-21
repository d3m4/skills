# Paleta e tipografia

Fonte única de cores, tamanhos e traços. Extraída do canvas de referência (`assets/frontend-runbook-example.excalidraw`), que usa a paleta padrão do Excalidraw. Não inventar cores fora desta tabela: se um conceito não se encaixa, usar o papel mais próximo e explicar na legenda.

Para trocar o visual de todos os diagramas, editar só este arquivo.

## Fluxo

| Papel | `strokeColor` | `backgroundColor` | `strokeStyle` | Texto |
|---|---|---|---|---|
| Início, sucesso, confirmação | `#1e1e1e` | `#b2f2bb` | `solid` | `#1e1e1e` 17 |
| Ação do usuário ou retorno na UI | `#1e1e1e` | `#dbe4ff` | `solid` | `#1e1e1e` 17 |
| Processamento interno | `#1e1e1e` | `transparent` | `dashed` | `#1e1e1e` 17 |
| Decisão (`diamond`) | `#1e1e1e` | `#fff3bf` | `solid` | `#1e1e1e` 14 |
| Erro, impedimento, retorno negativo | `#e03131` | `#ffc9c9` | `solid` | `#c92a2a` 17 |
| Seta e rótulo de seta (`Sim`/`Não`) | `#1e1e1e` | `transparent` | `solid` | `#1e1e1e` 13 |

Erro e sucesso não podem depender só da cor: o texto do nó diz o que aconteceu ("Exibe erros nos campos", "Confirma ativação").

## Páginas e listagens (wireframes)

| Papel | `strokeColor` | `backgroundColor` | `strokeWidth` |
|---|---|---|---|
| Moldura de página | `#1e1e1e` | `#f8f9fa` | 2 |
| Input, select, textarea | `#1e1e1e` | `#ffffff` | 1 |
| Botão primário (`Salvar`, `+ Novo`) | `#1971c2` | `#a5d8ff` | 2 |
| Botão secundário (`Cancelar`, `Validar`, ações por linha) | `#495057` | `#f1f3f5` | 2 |
| Seção repetível dentro da página | `#1e1e1e` | `#fff9db` | 2, `dashed` |
| Cabeçalho de tabela | `#1e1e1e` | `#e7f5ff` | 1 |
| Linha de tabela | `#1e1e1e` | `#f8f9fa` | 1 |
| Badge `Ativo`, método HTTP, página atual | `#2b8a3e` | `#d3f9d8` | 1 |
| Badge `Inativo` | `#868e96` | `#e9ecef` | 1 |
| Painel de resultado positivo | `#2f9e44` | `#d3f9d8` | 2 |
| Nota de estados/contrato (rodapé de área) | `#f08c00` | `#fff9db` | 2, `dashed` |

## Gaps

| Papel | `strokeColor` | `backgroundColor` | `strokeStyle` |
|---|---|---|---|
| Gap crítico (segurança, contradição entre fontes) | `#e03131` | `#ffc9c9` | `solid` |
| Gap ou necessidade comum | `#1e1e1e` | `#dbe4ff` | `solid` |
| Decisão de produto em aberto | `#1e1e1e` | `transparent` | `dashed` |

## Rastreabilidade

| Papel | `strokeColor` | `backgroundColor` | Texto |
|---|---|---|---|
| Marcador `GAP-n` no fluxo (abaixo do nó, ligado por seta curta) | `#9c36b5` | `#f3d9fa` | `#862e9c` 12 |
| Código de página `P1…Pn` (no título do wireframe e no nó) | `#1971c2` | `#e7f5ff` | `#1971c2` 12 |

## Texto

| Uso | Cor | `fontSize` |
|---|---|---|
| Título do canvas | `#1e1e1e` | 30 |
| Título de área (Páginas, Listagens, Gaps) | `#1e1e1e` | 27 |
| Título de página/listagem | `#1e1e1e` | 22–23 |
| Rótulo de nó do fluxo, legenda | `#1e1e1e` | 17 |
| Escopo/subtítulo | `#495057` | 16 |
| Rótulo de campo, célula de tabela | `#1e1e1e` | 12–13 |
| Breadcrumb, ajuda contextual | `#868e96` | 13 |
| Placeholder (exemplo realista dentro do campo) | `#868e96` | 12 |
| Contagem de resultados, nota de rodapé | `#495057` | 13 |
| Mensagem de erro de campo | `#c92a2a` | 13 |
| Título de nota de estados | `#e67700` | 20 |

## Traço e fonte

- `fontFamily: 5` (Excalifont), `roughness: 1`, `opacity: 100` em tudo.
- `strokeWidth: 2` para nós, setas e botões; `1` para inputs, linhas de tabela e badges.
- `roundness: {"type": 3}` em retângulos; `{"type": 2}` em setas; `null` em losangos.
- `viewBackgroundColor: "#ffffff"`.
