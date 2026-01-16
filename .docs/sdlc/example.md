# Exemplo

## Sistema de Alerta de Volatilidade para Traders

```bash
/sdlc-start "Sistema de alertas em tempo real para volatilidade de ativos da B3"
```

### 🔄 Fluxo Completo das 9 Fases (totalmente automatizado)

---

**📋 Fase 0 - Preparação (intake-analyst, compliance-guardian)**
```yaml
intake_analysis:
  title: "Sistema de Alertas de Volatilidade B3"
  complexity_level: 2  # BMAD Method
  domain: "Financial Markets / Trading"
  compliance_requirements:
    - "CVM Instrução 617 - Registro de operações"
    - "LGPD - Dados de clientes"
    - "Bacen Resolução 4893 - Cibersegurança"
  stakeholders:
    - Mesa de Operações
    - Compliance
    - TI/Infraestrutura
```

---

**🔍 Fase 1 - Discovery (domain-researcher, doc-crawler, rag-curator)**
```yaml
research_findings:
  market_data_sources:
    - "B3 Market Data Feed (UMDF)"
    - "Bloomberg Terminal API"
    - "Refinitiv Eikon"
  volatility_models:
    - "GARCH (Generalized Autoregressive Conditional Heteroskedasticity)"
    - "VIX adaptado para IBOV"
    - "ATR (Average True Range)"
  competitors:
    - "TradingView Alerts"
    - "Bloomberg ALRT"
  tech_stack_recommendation:
    streaming: "Apache Kafka"
    processing: "Apache Flink"
    storage: "TimescaleDB"
```

---

**📝 Fase 2 - Requirements (product-owner, requirements-analyst, ux-writer)**
```yaml
user_story:
  id: "US-001"
  persona: "Trader de Renda Variável"
  story: "Como trader, quero receber alertas quando a volatilidade 
          de um ativo ultrapassar um threshold definido por mim, 
          para que eu possa ajustar minha posição rapidamente"
  acceptance_criteria:
    - given: "Estou monitorando PETR4"
      when: "A volatilidade intraday supera 3 desvios padrão"
      then: "Recebo alerta via push notification em < 500ms"
    - given: "Defini threshold de 2.5% para VALE3"
      when: "Variação atinge 2.5% em janela de 5 minutos"
      then: "Sistema dispara alerta com preço atual e variação"
  security_requirements:
    - "Autenticação via certificado digital ICP-Brasil"
    - "Criptografia TLS 1.3 para dados em trânsito"
    - "Logs de auditoria para compliance CVM"
```

---

**🏗️ Fase 3 - Architecture (system-architect, threat-modeler, iac-engineer)**
```yaml
architecture_decision_record:
  id: "ADR-001"
  title: "Event-Driven Architecture para Processamento de Market Data"
  context: "Precisamos processar ~50.000 eventos/segundo do feed da B3"
  decision: "Usar Apache Kafka + Flink para streaming de eventos"
  consequences:
    positive:
      - "Latência < 100ms end-to-end"
      - "Escalabilidade horizontal"
      - "Replay de eventos para backtesting"
    negative:
      - "Complexidade operacional maior"
      - "Custo de infraestrutura ~R$15k/mês"

threat_model:
  asset: "Dados de mercado e posições de clientes"
  threats:
    - type: "Spoofing"
      description: "Atacante injeta dados falsos de cotação"
      mitigation: "Validação de assinatura digital do feed B3"
      risk_level: "HIGH"
    - type: "Information Disclosure"
      description: "Vazamento de estratégias de trading"
      mitigation: "Criptografia at-rest com AWS KMS"
      risk_level: "CRITICAL"

iac_output:
  provider: "AWS"
  resources:
    - "MSK (Managed Kafka) - 3 brokers"
    - "Kinesis Data Analytics (Flink)"
    - "RDS PostgreSQL + TimescaleDB"
    - "API Gateway + Lambda"
```

---

**📅 Fase 4 - Planning (delivery-planner)**
```yaml
sprint_plan:
  sprint_1:
    goal: "MVP - Ingestão de dados e cálculo de volatilidade"
    duration: "2 semanas"
    tasks:
      - "Conectar ao UMDF da B3"
      - "Implementar cálculo de volatilidade (ATR)"
      - "Armazenar em TimescaleDB"
    story_points: 21
  
  sprint_2:
    goal: "Sistema de alertas e notificações"
    duration: "2 semanas"
    tasks:
      - "Engine de regras para thresholds"
      - "Push notifications (Firebase)"
      - "Dashboard de configuração"
    story_points: 18
  
  sprint_3:
    goal: "Compliance e produção"
    duration: "2 semanas"
    tasks:
      - "Logs de auditoria CVM"
      - "Autenticação ICP-Brasil"
      - "Testes de carga (50k eventos/s)"
    story_points: 13
```

---

**💻 Fase 5 - Implementation (code-author, code-reviewer, test-author)**
```python
# Exemplo de código gerado pelo code-author
# filepath: src/volatility/calculator.py

from dataclasses import dataclass
from datetime import datetime
from typing import List
import numpy as np

@dataclass
class MarketTick:
    symbol: str
    price: float
    volume: int
    timestamp: datetime

class VolatilityCalculator:
    """Calcula volatilidade usando ATR (Average True Range)."""
    
    def __init__(self, window_size: int = 14):
        self.window_size = window_size
        self._price_history: dict[str, List[float]] = {}
    
    def update(self, tick: MarketTick) -> float | None:
        """Atualiza histórico e retorna volatilidade atual."""
        if tick.symbol not in self._price_history:
            self._price_history[tick.symbol] = []
        
        history = self._price_history[tick.symbol]
        history.append(tick.price)
        
        if len(history) < self.window_size:
            return None
        
        # Manter apenas janela necessária
        if len(history) > self.window_size:
            history.pop(0)
        
        return self._calculate_atr(history)
    
    def _calculate_atr(self, prices: List[float]) -> float:
        """Calcula Average True Range."""
        true_ranges = []
        for i in range(1, len(prices)):
            high_low = abs(prices[i] - prices[i-1])
            true_ranges.append(high_low)
        
        return np.mean(true_ranges)
```

```yaml
# Teste gerado pelo test-author
test_cases:
  - name: "test_volatility_spike_triggers_alert"
    given: "PETR4 com histórico de 14 ticks estável"
    when: "Novo tick com variação de 5%"
    then: "ATR ultrapassa threshold e alerta é disparado"
    
  - name: "test_latency_under_500ms"
    given: "Sistema sob carga de 50k eventos/segundo"
    when: "Evento de alta volatilidade é recebido"
    then: "Alerta é entregue em menos de 500ms"
```

---

**🔍 Fase 6 - Quality (qa-analyst, security-scanner, performance-analyst)**
```yaml
quality_report:
  summary:
    status: approved
  
  test_execution:
    unit_tests: { passed: 47, failed: 0 }
    integration_tests: { passed: 12, failed: 0 }
    e2e_tests: { passed: 8, failed: 0 }
    coverage: "87%"
  
  security_scan:
    sast_findings: 0
    sca_vulnerabilities:
      critical: 0
      high: 0
      medium: 2  # Dependências com patches disponíveis
    secrets_detected: 0
  
  performance:
    latency_p99: "320ms"
    throughput: "52,000 events/sec"
    memory_usage: "2.1GB"
```

---

**🚀 Fase 7 - Release (release-manager, cicd-engineer, doc-generator)**
```yaml
release:
  version: "1.0.0"
  changelog:
    - "Ingestão de market data via UMDF B3"
    - "Cálculo de volatilidade ATR em tempo real"
    - "Alertas push com latência < 500ms"
    - "Dashboard de configuração de thresholds"
    - "Logs de auditoria para compliance CVM"
  
  deployment:
    environment: "production"
    strategy: "blue-green"
    rollback_plan: "Automático se error_rate > 1%"
  
  documentation_generated:
    - "README.md"
    - "API Reference (OpenAPI 3.0)"
    - "Runbook de Operações"
    - "Guia de Compliance CVM"
```

---

**📊 Fase 8 - Operations (incident-commander, metrics-analyst, observability-engineer)**
```yaml
operational_metrics:
  dora:
    deployment_frequency: "3x por semana"
    lead_time: "2 dias"
    change_failure_rate: "4%"
    mttr: "15 minutos"
  
  business:
    alerts_sent_daily: 1247
    avg_alert_latency: "280ms"
    false_positive_rate: "2.3%"
    active_users: 342
  
  observability:
    dashboards:
      - "Grafana: Latência de Alertas"
      - "Grafana: Volume de Market Data"
      - "Grafana: Saúde do Kafka"
    alerts:
      - "PagerDuty: Latência > 1s"
      - "Slack: Error rate > 0.5%"
```

---

### 🎯 Resumo do Fluxo

```
┌─────────────────────────────────────────────────────────────────────┐
│  /sdlc-start "Sistema de alertas de volatilidade B3"                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Fase 0: Compliance CVM/LGPD identificado ✓                        │
│  Fase 1: Kafka + Flink + TimescaleDB selecionados ✓                │
│  Fase 2: 5 User Stories + Security Requirements ✓                  │
│  Fase 3: ADR Event-Driven + Threat Model ✓                         │
│  Fase 4: 3 Sprints planejados (52 story points) ✓                  │
│  Fase 5: Código + Testes implementados ✓                           │
│  Fase 6: 87% coverage, 0 vulnerabilidades críticas ✓               │
│  Fase 7: v1.0.0 deployed (blue-green) ✓                            │
│  Fase 8: Métricas DORA + Dashboards operacionais ✓                 │
│                                                                     │
│  🏁 Sistema em produção processando 50k eventos/segundo            │
└─────────────────────────────────────────────────────────────────────┘
```
