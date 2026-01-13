<!-- /engineering-playbook/manual-desenvolvimento/testes.md -->

# Testes

Testes existem para reduzir risco.
Não existem para inflar métricas.

A estratégia aqui é baseada em:
- criticidade do comportamento
- custo de falha
- probabilidade de regressão

## 1. Regra principal

Teste o que pode quebrar com impacto real.

- caminhos críticos
- validações de entrada
- regras de negócio relevantes
- integrações
- transformações de dados com efeito cascata

Evite testar detalhes internos sem necessidade.
Teste frágil custa mais do que ajuda.

## 2. Pirâmide pragmática

Em geral:
- mais testes unitários para lógica e regras
- testes de integração para contratos e integrações reais
- poucos e2e para fluxos críticos, bem escolhidos

Se o sistema for altamente distribuído, testes de contrato ganham importância.

## 3. Quando teste unitário é suficiente

- lógica pura
- regras de negócio bem isoladas
- validações e transformações
- cálculos e decisões determinísticas

## 4. Quando teste de integração é obrigatório

- acesso a banco
- acesso a fila
- chamada de serviço externo
- autenticação e autorização
- serialização e contratos de API

Se a falha provável está na fronteira, teste na fronteira.

## 5. Quando teste e2e é obrigatório

- fluxos críticos de pessoas usuárias
- pagamentos e eventos financeiros
- autenticação e jornada principal
- operações com grande risco de regressão

Poucos testes e2e bons são melhores do que muitos testes e2e instáveis.

## 6. Cobertura

Cobertura é indicador, não objetivo.

A meta real é:
- cobrir risco
- reduzir regressão
- acelerar refatoração segura

Se alguém estiver buscando cobertura alta sem critério:
- o sistema tende a piorar, não melhorar

## 7. Testes e agentes

Quando agentes automatizados gerarem código:
- exigir que os testes acompanhem a mudança
- não aceitar código sem mitigação quando o risco é claro
- preferir testes claros a testes complexos

