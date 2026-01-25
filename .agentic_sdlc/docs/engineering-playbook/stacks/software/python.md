<!-- /engineering-playbook/stacks/software/python.md -->

# Stack Software. Python

Python aqui é tratado como ferramenta excelente para alguns contextos e ruim para outros.
O objetivo é reduzir uso por impulso.

## Status

Recomendado para:
- automação e tooling
- pipelines e jobs
- prototipagem exploratória
- componentes de dados e analytics

Não é padrão para backend de produto quando dotnet atende.

## Quando usar

- scripts e automações de engenharia
- ETL e processamento de dados
- jobs assíncronos
- notebooks e exploração de dados
- ferramentas internas, onde velocidade de iteração é prioridade e risco é controlado

## Quando não usar

- serviços de negócio críticos sem disciplina forte de tipagem, testes e operação
- componentes onde performance previsível é requisito duro e comprovado
- sistemas que exigem padronização rígida de runtime e dependências sem maturidade operacional

## Padrões mínimos

- gerenciamento de dependências com lock file
- ambiente reprodutível
- formatador e linter automáticos
- testes mínimos compatíveis com risco

## Tipagem

Quando o contexto exigir manutenibilidade e refatoração segura:
- adotar tipagem gradual
- evitar interfaces implícitas frágeis

## Segurança

- cuidado com dependências e supply chain
- segredos fora do repo
- validação de entrada também em tooling

## Observabilidade

Para jobs e pipelines:
- logs estruturados
- métricas simples de sucesso e falha
- alertas quando houver operação recorrente

## Exceções

Uso de Python como backend principal de produto:
- exige decisão registrada
- exige plano de operação
- exige critério de rollback

