<!-- /engineering-playbook/stacks/software/dotnet.md -->

# Stack Software. Dotnet

Este documento descreve o padrão de desenvolvimento para serviços em dotnet.

## Status

Preferida como padrão para backend de produtos e serviços.

## Quando usar

- serviços de negócio
- APIs internas e externas
- integrações corporativas
- aplicações onde manutenção e legibilidade são prioridade
- cenários onde ecossistema dotnet reduz custo e risco

## Quando não usar

- protótipos descartáveis onde o custo de setup não se paga
- processamento altamente especializado que exija performance extrema e comprovada
  nesses casos, considerar exceção isolada com decisão registrada

## Padrões mínimos

- estilo de arquitetura definido por contexto, mas com fronteiras claras
- logging estruturado para caminhos críticos
- tratamento consistente de erro
- validação de entrada
- testes compatíveis com risco

## Organização de solução

Sugestão prática, sem impor formato único:

- src
  - serviços e bibliotecas
- tests
  - unit
  - integration
- docs
  - ADRs e especificações relevantes

## APIs e contratos

- contratos devem ser explícitos
- mudanças incompatíveis precisam ser comunicadas e versionadas
- quando houver consumidor externo, considerar teste de contrato

## Performance

- medir antes de otimizar
- preferir melhorar algoritmo e arquitetura
- evitar micro otimizações sem evidência

## Segurança

- autenticação e autorização devem ser explícitas
- segredos nunca no repositório
- dependências precisam ser monitoradas

## Observabilidade

Mínimo recomendado:

- logs estruturados com correlação quando houver requisição
- métrica de taxa de erro e latência em endpoints críticos
- tracing quando houver múltiplos serviços

## Exceções

Qualquer decisão de trocar linguagem ou runtime:
- exige justificativa mensurável
- exige isolamento por fronteira
- exige registro

