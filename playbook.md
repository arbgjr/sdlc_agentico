# Playbook de Desenvolvimento – MVP

Este repositório define o **Playbook de Desenvolvimento**.
Ele descreve como o desenvolvimento de software é realizado hoje, quais são os limites aceitáveis e quais expectativas mínimas devem ser atendidas.

Este playbook não descreve ferramentas específicas, nem pipelines, nem arquiteturas detalhadas. Ele define princípios, padrões e práticas que orientam decisões humanas e automatizadas.

O playbook é um artefato vivo. Toda mudança deve ser registrada, discutida e versionada.

---

## Para que este playbook existe

* Criar uma linguagem comum entre pessoas e agentes automatizados
* Reduzir decisões implícitas e improvisadas
* Tornar explícito o que é aceitável em termos de qualidade e responsabilidade
* Servir como referência única para decisões recorrentes

---

## O que este playbook não é

* Não é um manual de ferramentas
* Não é documentação de produto
* Não é uma coleção de boas intenções
* Não substitui pensamento crítico

---

## Estrutura do playbook

* principles: valores técnicos que orientam decisões
* standards: regras mínimas obrigatórias
* practices: formas recomendadas de trabalho
* adr: registro formal de decisões técnicas
* governance: como este playbook evolui

---

# Principles

## Qualidade é responsabilidade de quem cria

Quem escreve código é responsável pela sua qualidade do início ao fim.
Testes, observabilidade e clareza fazem parte da entrega.
Problemas não devem ser empurrados para etapas posteriores.

## Mudanças pequenas são preferíveis a grandes

Mudanças menores reduzem risco, facilitam revisão e aceleram aprendizado.
Grandes mudanças só são aceitáveis quando justificadas explicitamente.

## Decisões técnicas devem ser registradas

Decisões relevantes não devem ficar apenas em conversas ou memória.
Toda decisão que afeta manutenção, escala ou custo deve ser registrada como ADR.

## Automatização antes de escala

Processos manuais só escalam até um limite.
Antes de crescer volume, automatizar verificações e controles.

## Observabilidade faz parte da entrega

Não é aceitável entregar algo que não pode ser observado.
Logs, métricas ou sinais mínimos devem existir desde a primeira versão.

---

# Standards

## Qualidade de código

Um trabalho só pode ser considerado concluído quando:

* O código é legível e compreensível
* Existe teste compatível com o risco da mudança
* O comportamento principal é observável
* Não há violações conhecidas dos princípios deste playbook

Mudanças que introduzem dívida técnica devem ser explicitamente registradas.

---

## Versionamento

O versionamento deve permitir identificar:

* Mudanças compatíveis
* Mudanças incompatíveis
* Correções

Toda mudança incompatível deve ser comunicada claramente.

---

## System design e ADR

System design deve ser executado e registrado quando a mudança alterar fronteiras do sistema, integrações, dados, requisitos não funcionais relevantes ou o modo de operação.

Nesses casos:

* Deve existir pelo menos 1 ADR descrevendo a decisão central
* Deve existir observabilidade mínima definida antes do deploy
* Deve existir um plano de rollout e reversão compatível com o risco

---

# Practices

## System design

System design é a prática de definir, de forma explícita e verificável, como o sistema vai atender o objetivo com o menor risco possível.

Esta prática é obrigatória quando qualquer item abaixo estiver presente:

* Novo serviço, novo domínio, novo produto ou novo fluxo crítico
* Mudança relevante em integrações, fronteiras ou contratos
* Mudança relevante em dados, consistência ou transações
* Requisitos não funcionais que afetem desenho, por exemplo latência, disponibilidade, custo, privacidade, auditoria
* Alterações que mudem estratégia de resiliência, escalabilidade ou observabilidade

### Saídas mínimas

1. Uma visão de alto nível do sistema
   Componentes principais e responsabilidades

2. Fronteiras e integrações
   O que o sistema consome e o que expõe

3. Dados e consistência
   Entidades relevantes, fontes de verdade e decisões de consistência

4. Requisitos não funcionais selecionados
   Apenas os que realmente impactam desenho

5. Riscos principais e mitigação
   Top 3 a top 5 riscos, com plano de redução

6. Decisões registradas em ADR
   Pelo menos 1 ADR para a decisão central, e outros quando necessário

### Fluxo mínimo

1. Definir objetivo e escopo
   O que entra e o que não entra

2. Identificar pessoas usuárias, atores e integrações

3. Listar requisitos não funcionais relevantes

4. Propor uma arquitetura de alto nível

5. Registrar decisões em ADR

6. Planejar rollout e validação
   Observabilidade mínima, feature flags quando fizer sentido, e plano de reversão

---

## Code Review

O objetivo do code review é reduzir risco e compartilhar entendimento.

Foco principal:

* Clareza da solução
* Aderência aos princípios
* Riscos introduzidos

O review não é espaço para preferência pessoal ou estilo subjetivo.

---

## Resposta a incidentes

Um incidente é qualquer situação que cause impacto real a pessoas usuárias ou ao negócio.

Diante de um incidente:

* Priorizar estabilização
* Comunicar o impacto de forma clara
* Registrar o ocorrido

Após o incidente, avaliar se ajustes no playbook ou novos ADRs são necessários.

---

# ADR

## Template de ADR

Título

Contexto
Descrever o problema e as restrições.

Decisão
Descrever claramente o que foi decidido.

Consequências
Descrever impactos positivos e negativos.

Status
Proposto, aceito, rejeitado ou descontinuado.

---

# Governance

## Como mudar este playbook

* Qualquer pessoa pode propor mudanças
* Mudanças devem ser feitas via pull request
* Alterações em standards e principles exigem revisão explícita
* O histórico de mudanças deve ser preservado

Este playbook entra em vigor a partir da sua aprovação no repositório.

---

## Aprovação de ADR e uso por agentes

### Papéis

* Pessoas mantenedoras do playbook
  Responsáveis por aprovar mudanças em principles, standards, e ADRs de alto impacto

* Pessoas contribuidoras
  Podem propor ADRs e mudanças via pull request

* Agentes automatizados
  Podem propor ADRs e mudanças via pull request, mas seguem regras de aprovação

### Regras de aprovação

1. ADR pode ser aceito sem revisão humana apenas quando todos os itens abaixo forem verdadeiros

* Escopo limitado e reversível
* Sem impacto regulatório ou jurídico
* Sem mudança de dados sensível ou política de retenção
* Sem mudança de fronteiras externas, contratos públicos, ou integrações críticas
* Sem aumento material de custo recorrente
* Observabilidade mínima e plano de reversão descritos no ADR

2. Revisão humana é obrigatória quando qualquer item abaixo ocorrer

* Mudança de requisitos não funcionais com impacto relevante, por exemplo disponibilidade, latência, auditoria, privacidade, custo
* Criação ou alteração de contrato externo
* Mudança de modelo de dados com risco de migração, consistência, ou perda
* Introdução de nova dependência central, nova linguagem, nova plataforma, ou nova forma de deploy
* Qualquer decisão classificada como alta criticidade

### Criticidade

* Baixa
  Mudanças internas e reversíveis, baixo risco

* Média
  Mudanças com impacto limitado em operação, custo ou dados

* Alta
  Mudanças que afetam operação, segurança, dados, custo recorrente ou contratos

A criticidade deve ser declarada no ADR.

---

## Onde colocar detalhes, tecnologia e especificidades

Este playbook separa conteúdo por intenção, para evitar mistura e confusão.

### Documento principal, README

O README explica:

* o que é o playbook
* para quem ele existe
* como navegar
* como propor mudanças

O README não deve conter regras detalhadas nem escolhas de tecnologia.

### principles

Vai aqui o que é estável e orienta decisões em qualquer stack.
Exemplo, qualidade, mudanças pequenas, decisões registradas.

### standards

Vai aqui o que é obrigatório e pode ser cobrado.
Exemplo, critérios mínimos de aceite, quando ADR é obrigatório.

### practices

Vai aqui como o trabalho é feito no dia a dia.
Exemplo, system design, code review, resposta a incidentes.

### adr

Vai aqui toda decisão relevante.
Se a decisão muda o modo de operar, manter ou evoluir o sistema, ela deve virar ADR.

### Onde entram linguagem, cloud, tools, libs

Esses itens raramente são standards universais. Em geral, eles entram como ADR.

Use este critério:

* Se for uma escolha que pode mudar no tempo, e depende de contexto, registre como ADR
* Se for uma regra mínima independente de tecnologia, registre como standard
* Se for orientação de trabalho, registre como practice

Sugestão prática para o repositório

* Criar uma pasta chamada stack apenas quando existir demanda real
* Dentro dela, manter documentos curtos, referenciados por ADR

Exemplo de estrutura futura, quando necessário

stack/
platform.md
languages.md
libraries.md
tooling.md

Regra

Escolha de stack deve sempre apontar para um ADR que justifique a decisão.

---

## Quando criar novos documentos

Crie um novo documento quando:

* o assunto tem vida própria e vai mudar ao longo do tempo
* o tema já está grande o suficiente para atrapalhar leitura
* existe necessidade de vincular o tema a ADRs específicos

Evite criar documentos novos quando:

* a informação é pequena e cabe como seção
* o tema ainda não é usado na prática

---

## Critério de qualidade do próprio playbook

Toda página do playbook deve:

* ser acionável
* evitar ambiguidade
* separar obrigação de recomendação
* indicar quando ADR é necessário
