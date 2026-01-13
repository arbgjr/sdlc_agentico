# Governance - Como Este Manual Evolui

## Como mudar este manual

- Qualquer pessoa pode propor mudancas
- Mudancas devem ser feitas via pull request
- Alteracoes em standards e principios exigem revisao explicita
- O historico de mudancas deve ser preservado

## Papeis

### Pessoas mantenedoras

Responsaveis por aprovar mudancas em:
- principles
- standards
- ADRs de alto impacto

### Pessoas contribuidoras

Podem propor ADRs e mudancas via pull request.

### Agentes automatizados

Podem propor ADRs e mudancas via pull request, mas seguem regras de aprovacao.

## Regras de aprovacao

### ADR pode ser aceito sem revisao humana quando:

- Escopo limitado e reversivel
- Sem impacto regulatorio ou juridico
- Sem mudanca de dados sensivel ou politica de retencao
- Sem mudanca de fronteiras externas, contratos publicos, ou integracoes criticas
- Sem aumento material de custo recorrente
- Observabilidade minima e plano de reversao descritos

### Revisao humana e obrigatoria quando:

- Mudanca de requisitos nao funcionais com impacto relevante
- Criacao ou alteracao de contrato externo
- Mudanca de modelo de dados com risco
- Introducao de nova dependencia central, nova linguagem, nova plataforma
- Qualquer decisao classificada como alta criticidade

## Criticidade

- **Baixa**: Mudancas internas e reversiveis, baixo risco
- **Media**: Mudancas com impacto limitado em operacao, custo ou dados
- **Alta**: Mudancas que afetam operacao, seguranca, dados, custo recorrente ou contratos

A criticidade deve ser declarada no ADR.

## Criterio de qualidade

Toda pagina do manual deve:

- ser acionavel
- evitar ambiguidade
- separar obrigacao de recomendacao
- indicar quando ADR e necessario
