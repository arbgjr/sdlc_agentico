<!-- /engineering-playbook/README.md -->

# Engineering Playbook

Este repositório organiza o que é esperado no desenvolvimento de software, em duas camadas.

1. Manual de Desenvolvimento
   Regras e práticas operacionais que funcionam no dia a dia.
   Deve ser acionável e cobravel.

2. Stacks
   Catálogo de referências técnicas adotadas ou recomendadas no momento.
   Não é um conjunto de ordens. É o ponto de partida. Exceções seguem decisão registrada.

Este repositório existe para reduzir variabilidade, aumentar previsibilidade e permitir que pessoas e agentes automatizados atuem com o mesmo entendimento.

## Como navegar

- Manual de Desenvolvimento
  - README: visão geral e como usar
  - princípios: guias de decisão estáveis
  - qualidade: critérios mínimos e gates humanos
  - testes: estratégia pragmática

- Stacks
  - README: como o catálogo funciona e como evolui
  - software: linguagens e frameworks
  - dados: plataformas e práticas de dados e analytics
  - devops: CI CD, observabilidade e segurança

## O que entra onde

Regra simples:

- Se for estável e vale em qualquer stack, entra no Manual.
- Se for escolha que pode mudar no tempo e depende de contexto, entra em Stacks e deve apontar para uma decisão registrada.
- Se for regra obrigatória, precisa ficar explícito como obrigatória, com critério de verificação.

## Como evoluir

Mudanças neste repositório devem ser feitas por pull request.

- Mudanças no Manual exigem revisão de pessoas mantenedoras.
- Mudanças em Stacks exigem, no mínimo:
  - motivação clara
  - impacto esperado
  - e link para decisão registrada, quando aplicável

## Relação com SDLC agêntico

O SDLC agêntico usa este repositório como fonte de regras e referências.

- Agentes consultam o Manual para saber o que é aceitável.
- Agentes consultam Stacks para escolher defaults e reduzir retrabalho.
- Quando uma escolha relevante aparecer, a decisão deve ser registrada, não só repetida em conversas.

