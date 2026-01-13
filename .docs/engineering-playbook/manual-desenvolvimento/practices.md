# Practices - Formas de Trabalho

Practices sao formas recomendadas de trabalho.
Nao sao regras absolutas, mas reduzem risco e retrabalho.

## System Design

System design e a pratica de definir, de forma explicita e verificavel, como o sistema vai atender o objetivo com o menor risco possivel.

### Quando e obrigatorio

- Novo servico, novo dominio, novo produto ou novo fluxo critico
- Mudanca relevante em integracoes, fronteiras ou contratos
- Mudanca relevante em dados, consistencia ou transacoes
- Requisitos nao funcionais que afetem desenho (latencia, disponibilidade, custo, privacidade, auditoria)
- Alteracoes que mudem estrategia de resiliencia, escalabilidade ou observabilidade

### Saidas minimas

1. Visao de alto nivel do sistema
   - Componentes principais e responsabilidades

2. Fronteiras e integracoes
   - O que o sistema consome e o que expoe

3. Dados e consistencia
   - Entidades relevantes, fontes de verdade e decisoes de consistencia

4. Requisitos nao funcionais selecionados
   - Apenas os que realmente impactam desenho

5. Riscos principais e mitigacao
   - Top 3 a top 5 riscos, com plano de reducao

6. Decisoes registradas em ADR
   - Pelo menos 1 ADR para a decisao central

### Fluxo minimo

1. Definir objetivo e escopo
2. Identificar pessoas usuarias, atores e integracoes
3. Listar requisitos nao funcionais relevantes
4. Propor uma arquitetura de alto nivel
5. Registrar decisoes em ADR
6. Planejar rollout e validacao

## Code Review

O objetivo do code review e reduzir risco e compartilhar entendimento.

### Foco principal

- Clareza da solucao
- Aderencia aos principios
- Riscos introduzidos

O review nao e espaco para preferencia pessoal ou estilo subjetivo.

### Comentarios

Comentarios devem ser:
- objetivos
- respeitosos
- tecnicos

Evitar:
- debates de preferencia
- sugestoes que nao agregam valor
- bloqueios por estilo

## Resposta a Incidentes

Um incidente e qualquer situacao que cause impacto real a pessoas usuarias ou ao negocio.

### Durante o incidente

1. Priorizar estabilizacao
2. Comunicar o impacto de forma clara
3. Registrar o ocorrido

### Apos o incidente

- Avaliar se ajustes no playbook sao necessarios
- Avaliar se novos ADRs sao necessarios
- Documentar licoes aprendidas

## ADR - Template

```markdown
# Titulo

## Contexto
Descrever o problema e as restricoes.

## Decisao
Descrever claramente o que foi decidido.

## Consequencias
Descrever impactos positivos e negativos.

## Status
Proposto | Aceito | Rejeitado | Descontinuado
```
