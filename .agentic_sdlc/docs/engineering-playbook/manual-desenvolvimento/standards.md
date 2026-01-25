# Standards - Regras Minimas Obrigatorias

Standards sao regras que podem ser cobradas.
Se nao for atendido, bloqueia merge ou release.

## Qualidade de codigo

Um trabalho so pode ser considerado concluido quando:

- O codigo e legivel e compreensivel
- Existe teste compativel com o risco da mudanca
- O comportamento principal e observavel
- Nao ha violacoes conhecidas dos principios deste playbook

Mudancas que introduzem divida tecnica devem ser explicitamente registradas.

## Versionamento

O versionamento deve permitir identificar:

- Mudancas compativeis
- Mudancas incompativeis
- Correcoes

Toda mudanca incompativel deve ser comunicada claramente.

## System design e ADR

System design deve ser executado e registrado quando a mudanca alterar:

- fronteiras do sistema
- integracoes
- dados
- requisitos nao funcionais relevantes
- modo de operacao

Nesses casos:

- Deve existir pelo menos 1 ADR descrevendo a decisao central
- Deve existir observabilidade minima definida antes do deploy
- Deve existir um plano de rollout e reversao compativel com o risco

## O que bloqueia merge

- bug funcional
- problema de seguranca
- violacao clara deste manual
- codigo impossivel de manter

## O que nao bloqueia merge

- preferencias pessoais
- estilo quando nao ha padrao definido
- micro otimizacoes sem impacto real
