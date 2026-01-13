<!-- /engineering-playbook/stacks/devops/security.md -->

# Stack DevOps. Segurança

Segurança é parte do desenho e parte do pipeline.
Não é um relatório no final.

## Status

Referência para todos os projetos que vão a produção.

## Regras mínimas

- segredos fora do repositório
- validação de entrada em endpoints e integrações
- autenticação e autorização explícitas quando aplicável
- dependências monitoradas
- logs sem dados sensíveis

## Pipeline mínimo de segurança

Recomendado incluir:

- SAST quando aplicável
- SCA para dependências
- scan de secrets
- verificação de configurações inseguras
- política de bloqueio por severidade definida

## Threat modeling

Obrigatório quando:

- existe dado pessoal ou sensível
- existe endpoint público novo
- existe mudança em autenticação ou autorização
- existe mudança criptográfica
- existe integração crítica nova

## Menor privilégio

- acessos devem ser mínimos e auditáveis
- credenciais devem ter rotação quando aplicável

## Gestão de vulnerabilidades

- vulnerabilidade crítica não deve ser ignorada
- quando houver exceção, registrar motivo e prazo
- correção deve ter dono e plano

## Exceções

Exceções em segurança precisam ser raras.
Quando existirem, precisam ser registradas com:

- risco aceito
- justificativa
- mitigação temporária
- data limite

