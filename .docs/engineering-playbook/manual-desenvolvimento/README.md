<!-- /engineering-playbook/manual-desenvolvimento/README.md -->

# Manual de Desenvolvimento de Software

Este manual define práticas operacionais e padrões mínimos de qualidade para desenvolvimento.
Ele existe para orientar decisões técnicas do dia a dia e reduzir variabilidade entre times.

Este documento não é um guia acadêmico e não é um espaço para preferências pessoais.

## Objetivo

- Deixar explícito o que é aceitável como entrega
- Reduzir retrabalho causado por padrões implícitos
- Aumentar legibilidade e manutenibilidade
- Diminuir risco operacional com testes e observabilidade mínimos
- Padronizar como pessoas e agentes avaliam pronto ou não pronto

## Escopo

Este manual cobre:

- Princípios práticos de engenharia
- Critérios de qualidade e pronto
- Regras de revisão de código
- Testes como mitigação de risco

Este manual não cobre:

- Definições de stack, ferramentas, cloud ou bibliotecas
  Isso vive em /stacks como referência
- Documentação de produto
- Tutoriais longos de frameworks

## Como usar este manual

Use como referência em três momentos:

1. Antes de começar
   Para alinhar expectativas e riscos.

2. Durante code review
   Para avaliar o que bloqueia merge e o que é sugestão.

3. Antes de release
   Para garantir que o mínimo foi atendido.

## Documentos

- principios.md
  O que orienta decisoes em qualquer stack.

- standards.md
  Regras minimas obrigatorias que podem ser cobradas.

- practices.md
  Formas recomendadas de trabalho (system design, code review, incidentes).

- qualidade.md
  O minimo para aceitar uma entrega, e como lidar com excecoes.

- testes.md
  Estrategia pragmatica de testes baseada em risco.

- governance.md
  Como este manual evolui e quem aprova mudancas.

## Relação com Stacks

Stacks é catálogo de referência técnica.
Manual é regra e prática de trabalho.

Se houver conflito entre um documento de Stack e este manual:
- o manual vence
- e a stack deve ser corrigida

