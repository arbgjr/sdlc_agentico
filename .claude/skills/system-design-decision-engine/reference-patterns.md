# Padrões cobertos

Esta Skill usa 7 padrões recorrentes.

1. scaling-reads
Quando há muitas leituras, leituras repetidas, necessidade de latência baixa.

2. scaling-writes
Quando há muitas escritas, picos, eventos, contadores, ingestão.

3. long-running-tasks
Quando há operações demoradas, risco de timeout, processamento pesado.

4. real-time-updates
Quando há atualização em tempo real, interação bidirecional, push.

5. large-files
Quando há upload ou download de arquivos grandes, alto consumo de banda.

6. contention
Quando há disputa por recurso, concorrência sobre o mesmo registro, reserva.

7. multi-step-processes
Quando há fluxo em múltiplas etapas, falhas intermediárias, compensação.

Fonte de verdade
Os sinais, perguntas obrigatórias, decisões e falhas comuns estão em:
data/patterns/*.json
