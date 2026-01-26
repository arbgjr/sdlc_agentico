<!-- /engineering-playbook/stacks/devops/ci-cd.md -->

# Stack DevOps. CI CD

CI CD existe para reduzir risco e aumentar repetibilidade.
Pipeline não é decoração, é controle.

## Status

Referência para projetos com release recorrente.

## Quando usar

- qualquer serviço com deploy em produção
- qualquer biblioteca que seja consumida por múltiplos projetos
- qualquer automação relevante

## Regras mínimas

- build reprodutível
- testes automáticos compatíveis com risco
- verificação de secrets
- verificação de dependências
- artefato versionado

## Gates

Gates devem ser claros e verificáveis.
Exemplos de gates típicos:

- lint e formatação
- testes unitários e integração
- scan de dependências
- scan de secrets
- validação de infraestrutura quando houver IaC

## Branching

- branches devem refletir intenção, por exemplo feature e fix
- mudanças pequenas são preferíveis
- PR é o ponto de auditoria

## Releases

- versionamento deve indicar compatibilidade
- mudanças incompatíveis precisam de comunicação
- rollback deve ser previsto quando risco for alto

## Exceções

Desabilitar etapas do pipeline:
- exige justificativa
- exige registro
- exige data de reativação

