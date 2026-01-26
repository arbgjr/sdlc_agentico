<!-- /engineering-playbook/stacks/dados/analytics.md -->

# Stack Dados. Analytics

Analytics aqui significa gerar informação confiável para decisão.
O foco é evitar dashboards sem definição e métricas instáveis.

## Status

Referência para iniciativas de métricas de produto, operação e engenharia.

## Quando usar

- métricas de uso e comportamento de pessoas usuárias
- métricas operacionais
- métricas de engenharia, por exemplo DORA e SPACE
- relatórios recorrentes que influenciam decisões

## Quando não usar

- quando o objetivo ainda não é mensurável
- quando a coleta for invasiva sem justificativa
- quando não houver governança de quem consome e interpreta

## Regras mínimas

- definição formal de cada métrica
- fonte de verdade identificada
- periodicidade clara
- tratamento de dados faltantes
- versionamento de eventos quando aplicável

## Eventos e tracking

- eventos devem ter contrato
- nomes devem ser consistentes
- mudanças incompatíveis precisam ser comunicadas
- coletar apenas o necessário

## Qualidade

- validação de esquema
- detecção de duplicidade quando houver risco
- auditoria de mudanças em definições

## Privacidade

- coletar o mínimo
- anonimizar quando possível
- registrar base legal e restrições quando houver dado pessoal

## Observabilidade

- taxa de eventos por período
- atraso entre evento e disponibilidade no consumo
- falhas de pipeline e reprocessamento

