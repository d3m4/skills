---
name: discuta-comigo
description: Use quando o usuário quer pensar junto / refinar uma ideia, decisão ou problema através de perguntas antes de receber uma proposta — em vez de uma resposta imediata. O usuário passa a pergunta ou tema inicial. Trigger: /discuta-comigo
---

Conduza uma conversa estruturada de descoberta a partir de `$ARGUMENTS` (a pergunta ou tema inicial). O objetivo é **refinar a ideia junto com o usuário ANTES de propor qualquer coisa**, em rodadas de 4 perguntas de múltipla escolha.

## Princípio central

Não responda nem proponha de cara. Primeiro **entenda** — através de rodadas de perguntas — e só apresente a proposta quando o usuário liberar.

## Workflow obrigatório

1. **Contexto primeiro (rápido).** Use só o contexto **já acessível no workspace** (arquivos do projeto, repositório, a máquina/hardware). Se houver algo útil, analise brevemente ANTES da primeira rodada e mostre o achado em 2–4 linhas. **Não faça buscas externas (web) nesta etapa** e não invente. Sem contexto relevante, pule e siga.

2. **Rodada de 4 perguntas.** Faça **exatamente 4 perguntas, todas num único bloco** do seletor de múltipla escolha (ferramenta AskUserQuestion — ela aceita até 4 perguntas por bloco; preencha as 4). Cada pergunta:
   - cobre uma dimensão: **propósito, restrições, critérios de sucesso ou trade-offs** (na 1ª rodada, idealmente uma de cada; nas seguintes, ataque o que ficou em aberto);
   - tem **no máximo 3 opções de conteúdo + 1 saída opcional** (teto de 4 da ferramenta; o usuário sempre pode escrever "Outro");
   - escolha **um** estilo conforme o tipo:
     - **pergunta de decisão/trade-off** (você tem uma opinião): a 1ª opção é a **sua recomendação**, marcada "(Recomendado)". Não adicione "Não sei" aqui — a recomendação já cumpre esse papel.
     - **pergunta de levantamento** (fato sobre o usuário: hardware, orçamento, contexto): **não marque "(Recomendado)"** (você não pode recomendar o que ele já tem); ofereça as opções neutras + uma saída "Não sei / me ajude a descobrir".

3. **Incorpore as respostas.** Releia tudo (inclusive os textos livres), ajuste seu entendimento e **resuma em 1–2 linhas** o que mudou. Dúvida nova e importante vira pergunta da próxima rodada.

4. **Pergunta-ponte (obrigatória, chamada SEPARADA).** Depois do bloco de 4, faça **uma chamada nova** do seletor com **uma única pergunta**. Em vez de um genérico "mais 4 perguntas", **identifique os 2 maiores gaps** que ainda restam no seu entendimento e ofereça-os como **direções concretas e nomeadas** (você dirige, não o usuário). As opções:
   - **Mais 4 sobre {gap A}** → o tema mais importante que ainda ficou em aberto (descreva o gap em poucas palavras, ex.: "Mais 4 sobre orçamento e prazo").
   - **Mais 4 sobre {gap B}** → o segundo gap mais relevante.
   - **Já pode propor** → encerra as perguntas e vai à proposta.
   - A **saída "Outro"** automática da ferramenta cobre o *"mais 4 de: digite"* — o usuário escreve o tema que quiser e você abre uma rodada focada nisso.
   - **Qual marcar "(Recomendado)" (= 1ª opção):** se o entendimento ainda está imaturo, recomende o **gap A**; quando já estiver maduro (em geral após 2–3 rodadas), recomende **"Já pode propor"**.
   - Nunca enfie a ponte como 5ª opção do bloco anterior. Os gaps devem ser **reais e específicos desta conversa** — nada de rótulos genéricos como "mais detalhes".
   - Qualquer direção de "mais 4" (A, B ou digitada) → volte ao passo 2 com **4 perguntas novas focadas nesse tema** (nunca repita as já respondidas). "Já pode propor" → vá ao passo 5.

5. **Proposta.** Só agora apresente o desenho fechado: **2–3 abordagens com trade-offs e a sua recomendação liderando**, ou um plano direto se já estiver claro. Responda dúvidas pontuais e, se o usuário pedir, parta para a execução.

## Regras

- Sempre em **pt-BR**.
- **Exatamente 4 perguntas por rodada**, num bloco único de múltipla escolha — nunca soltas no texto, nunca 3, nunca 5.
- A **pergunta-ponte** é obrigatória ao fim de TODA rodada, sempre como chamada separada.
- "(Recomendado)" só em perguntas de **decisão/trade-off**, nunca em perguntas de **levantamento de fato** do usuário.
- **Nunca pule para a proposta** sem ao menos uma rodada + pergunta-ponte — exceto se o usuário pedir explicitamente (ex.: o próprio `$ARGUMENTS` já diz "só me proponha X" ou ele responde "pula as perguntas").
- **Recomende, não despeje opções**: lidere com a sua sugestão e o porquê.
- Não comece a implementar nada durante a discussão; o entregável é a proposta aprovada.

## Erros comuns

- Fazer 3 ou 5 perguntas. → São **exatamente 4** por rodada, em um bloco.
- Marcar "(Recomendado)" em pergunta sobre o que o usuário **tem/possui**. → Use opções neutras + saída "Não sei".
- Pôr "(Recomendado)" **e** "Não sei, recomende" na mesma pergunta. → Redundante; escolha um.
- Estourar o teto de 4 opções da ferramenta. → Máx. 3 de conteúdo + 1 saída.
- Embutir a pergunta-ponte no bloco das 4. → É uma **chamada separada**.
- Oferecer ponte genérica ("mais 4 perguntas"). → **Nomeie os 2 gaps** percebidos como direções concretas; o "Outro" cobre o tema digitado.
- Propor cedo demais ou nunca parar. → Só após a ponte liberar; sugira propor quando já entendeu o bastante.
