<!-- /engineering-playbook/stacks/devops/observability.md -->

# Stack DevOps. Observabilidade

Se não dá para observar, não dá para operar.

Observabilidade aqui inclui:
- logs
- métricas
- traces
- alertas
- runbooks mínimos

## Status

Referência para serviços e pipelines em operação.

## Mínimo obrigatório por serviço

- logs do caminho crítico com contexto suficiente para investigação
- registro explícito de erros
- correlação por requisição quando houver API
- métricas básicas de erro e latência para endpoints críticos

## Golden signals

Onde fizer sentido, acompanhar:

- latência
- tráfego
- erros
- saturação

## Tracing

Recomendado quando:

- existe encadeamento entre múltiplos serviços
- existe fila ou processamento assíncrono
- o caminho de requisição é complexo

## Alertas

Alertas precisam ter:

- condição clara
- severidade
- ação esperada
- link para runbook quando houver

Alerta que ninguém consegue agir é ruído.

## Runbooks

Para sistemas críticos, manter:

- como diagnosticar falha
- como mitigar
- como fazer rollback quando aplicável
- como validar retorno ao normal

## Exceções

Ausência de observabilidade em produção:
- deve ser tratada como risco
- deve virar item de backlog com prioridade compatível

