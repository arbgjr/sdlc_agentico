<!-- /engineering-playbook/manual-desenvolvimento/principios.md -->

# Princípios de Desenvolvimento

Estes princípios orientam decisões em qualquer stack e em qualquer contexto.

Eles não substituem pensamento crítico.
Eles existem para reduzir decisões ruins por impulso.

## 1. Tecnologia é meio, não fim

Escolhas tecnológicas precisam ser justificadas por impacto observável:
- risco reduzido
- custo menor
- manutenção mais simples
- desempenho necessário
- segurança melhor

Preferência pessoal não é justificativa.

## 2. Clareza vence elegância

Código é lido mais do que escrito.

- Prefira nomes explícitos a comentários explicativos
- Prefira estruturas simples a abstrações prematuras
- Evite truques e padrões que só uma parte do time entende

Se a solução precisa ser explicada demais, ela tende a ser frágil.

## 3. Mudanças pequenas são preferíveis

Mudanças pequenas:
- reduzem risco
- facilitam revisão
- aceleram feedback
- tornam rollback mais viável

Se uma mudança precisa ser grande:
- divida em etapas
- mantenha compatibilidade quando possível
- registre decisão e plano de rollout

## 4. Decisões relevantes precisam ser registradas

Quando uma decisão impacta manutenção, custo, operação, segurança ou dados:
- registre a decisão
- registre alternativas consideradas
- registre consequências

Decisão não registrada vira ruído e retrabalho.

## 5. Não otimizar antes de medir

Performance é requisito quando há meta e evidência.

Ordem de decisão:
1. medir
2. identificar gargalo
3. melhorar algoritmo e arquitetura
4. otimizar implementação
5. somente então considerar troca de linguagem ou stack

## 6. Qualidade é responsabilidade de quem cria

Quem entrega código entrega junto:
- o mínimo de testes compatíveis com risco
- observabilidade mínima do caminho crítico
- clareza suficiente para manutenção

Problemas não devem ser empurrados para depois como regra padrão.

## 7. Exceção sem registro vira dívida técnica

Se for necessário quebrar um padrão:
- justificar
- isolar impacto
- registrar
- definir data de reavaliação

Sem isso, a exceção vira padrão por acidente.

## 8. Segurança e privacidade fazem parte do desenho

Segurança não é fase final.

- ameaças precisam ser consideradas no desenho
- entradas precisam ser validadas
- segredos não podem aparecer no repositório
- acessos precisam seguir menor privilégio

Quando houver dado sensível ou risco regulatório:
- tratar como risco alto
- exigir revisão apropriada

