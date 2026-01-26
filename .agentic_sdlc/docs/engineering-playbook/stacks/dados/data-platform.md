<!-- /engineering-playbook/stacks/dados/data-platform.md -->

# Stack Dados. Data Platform

Este documento define referências para construção e operação de uma plataforma de dados.
O objetivo é evitar plataformas improvisadas e pipelines sem governança mínima.

## Status

Referência para produtos que tenham:
- ingestão recorrente de dados
- necessidade de qualidade e rastreabilidade
- analytics e consumo por múltiplos times
- requisitos de segurança e privacidade

## Quando usar

- quando houver múltiplas fontes e múltiplos consumidores
- quando dados precisarem de qualidade, lineage e auditoria
- quando houver necessidade de camadas e contratos claros

## Quando não usar

- para extrações pontuais ou descartáveis
- quando o custo da plataforma for maior do que o valor do uso
  nesse caso, usar solução simples e registrada

## Princípios mínimos

- dados com dono claro
- contratos de dados explícitos quando houver consumo recorrente
- separação entre ingestão e consumo
- governança mínima de acesso

## Camadas

Sugestão comum, ajustar conforme contexto:

- raw
  dados como recebidos, com rastreabilidade

- curated
  dados tratados, com qualidade e padronização

- serving
  dados preparados para consumo e performance

## Qualidade

Mínimos recomendados:

- validações de esquema
- validações de volume e anomalia quando houver histórico
- tratamento explícito de falhas
- reprocessamento definido

## Segurança e privacidade

- classificação de dados
- menor privilégio
- segregação por domínio quando necessário
- mascaramento e retenção quando aplicável

## Observabilidade

- métricas de sucesso e falha por pipeline
- tempo de execução
- atraso de dados
- alertas para falhas recorrentes

## Exceções

Qualquer quebra de governança por urgência:
- precisa de registro
- precisa de plano de correção
- precisa de reavaliação

