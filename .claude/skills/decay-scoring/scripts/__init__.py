"""
Decay Scoring - Sistema de pontuacao temporal para nodes de conhecimento.

Este pacote fornece ferramentas para:
- Calcular scores de decay baseados em idade, validacao e acesso
- Rastrear padroes de acesso aos nodes
- Gerar sugestoes de curadoria para conteudo obsoleto

Modulos:
    decay_calculator: Calculo de scores de decay
    decay_tracker: Rastreamento de acessos e validacoes
    decay_trigger: Geracao de sugestoes de curadoria
"""

__version__ = "1.0.0"
__all__ = ["decay_calculator", "decay_tracker", "decay_trigger"]
