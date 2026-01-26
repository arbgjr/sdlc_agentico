<!-- /engineering-playbook/manual-desenvolvimento/qualidade.md -->

# Qualidade

Qualidade aqui significa reduzir risco e aumentar previsibilidade de manutenção e operação.

Este documento define:
- critérios mínimos para aceitar uma entrega
- como conduzir code review
- quando bloquear merge
- como lidar com exceções

## 1. Definição mínima de pronto

Um trabalho só pode ser considerado concluído quando:

- O código é legível e compreensível
- O comportamento principal é observável de alguma forma
- Existe teste compatível com o risco
- Não há violações conhecidas dos princípios do manual
- Mudanças relevantes foram registradas como decisão quando aplicável

## 2. O que bloqueia merge

Bloqueia merge quando houver:

- bug funcional claro
- falha de segurança ou exposição de segredo
- violação do manual
- comportamento não observável em produção quando deveria ser
- ausência de teste onde o risco é evidente
- acoplamento excessivo ou alteração perigosa sem justificativa e sem isolamento

## 3. O que não bloqueia merge

Não bloqueia merge quando for:

- preferência pessoal de estilo
- micro otimização sem evidência
- sugestão de refino que pode virar issue futura
- debate de padrão que não está documentado

Se algo não está documentado, a ação correta é:
- propor uma melhoria no manual ou na stack
- e não travar a entrega por opinião

## 4. Exceções técnicas

Exceção só é aceitável quando:

- existe justificativa objetiva
- existe escopo bem definido
- existe isolamento com fronteiras claras
- existe registro do custo assumido
- existe data de reavaliação

Se não houver registro, a exceção é dívida técnica.

## 5. Registro do motivo quando há dívida consciente

Quando a decisão for aceitar dívida técnica:
- deixar explícito por que foi aceita
- qual risco está sendo assumido
- qual é o plano e quando será reavaliado

## 6. Observabilidade mínima

Todo serviço ou fluxo crítico deve ter, no mínimo:

- logs úteis no caminho de sucesso e falha
- correlação de requisições quando fizer sentido
- métricas mínimas de erro e latência, se houver API
- erro visível, não silencioso

Sem observabilidade, não existe operação confiável.

## 7. Critérios de qualidade para o próprio playbook

Todo documento deste repositório deve:

- ser acionável
- evitar ambiguidade
- separar obrigação de recomendação
- apontar para decisões quando depender de contexto

