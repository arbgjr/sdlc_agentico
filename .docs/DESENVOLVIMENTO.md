# Manual de Desenvolvimento de Software

## 1. Objetivo e escopo

Este manual define **práticas operacionais de desenvolvimento de software** que funcionam na prática.  
Ele existe para orientar decisões técnicas do dia a dia, reduzir variabilidade entre times e registrar padrões que já foram validados em projetos reais.

Este documento não é conceitual, não é acadêmico e não serve para debates de preferência pessoal.

---

## 2. Princípio de agnosticismo tecnológico

A tecnologia é um meio, não um fim.

A linguagem padrão de desenvolvimento é **C#**.  
Ela deve ser utilizada por padrão em novos sistemas e evoluções.

Outras linguagens só devem ser consideradas em **situações excepcionais**, quando houver **ganho técnico comprovável**, principalmente relacionado a performance.

Preferência pessoal, familiaridade prévia ou tendência de mercado **não são critérios válidos**.

---

## 3. Regra geral de escolha de linguagem

- Use C# como padrão
- Não troque de linguagem por suposição
- Meça antes de decidir
- Otimize algoritmo e arquitetura antes de trocar stack

Trocar de linguagem sem evidência mensurável é considerado erro técnico.

---

## 4. Exceções por necessidade de performance

O uso de uma linguagem diferente de C# só é permitido quando **todos** os critérios abaixo forem atendidos.

### 4.1 Gargalo comprovado

- O problema deve estar identificado por profiling ou métricas reais
- A medição deve ocorrer em ambiente representativo ou produção
- O gargalo deve ser claro em CPU, memória, latência ou throughput

### 4.2 Impacto relevante

- A melhoria esperada deve ser de **ordem de grandeza**
- Melhorias marginais não justificam troca de linguagem
- Referência mínima esperada: múltiplos de desempenho, não porcentagens pequenas

### 4.3 Limitação intrínseca da plataforma padrão

Antes da troca, deve estar comprovado que o problema **não pode ser resolvido** por:

- melhoria de algoritmo
- ajuste de arquitetura
- paralelismo ou concorrência
- caching
- uso adequado de recursos da plataforma C#

### 4.4 Isolamento técnico obrigatório

A exceção deve ser isolada de forma clara:

- fronteira explícita
- contrato bem definido
- baixo acoplamento com o restante do sistema
- possibilidade de substituição futura

### 4.5 Custo assumido conscientemente

Deve ficar claro o impacto em:

- build
- deploy
- observabilidade
- suporte
- conhecimento necessário no time

Se qualquer um desses pontos não for atendido, a decisão padrão é **não trocar de linguagem**.

---

## 5. Registro de exceções técnicas

Toda exceção deve ser documentada.

### Informações mínimas obrigatórias

- problema identificado
- métricas antes da mudança
- alternativa avaliada em C#
- motivo da inviabilidade na stack padrão
- métricas esperadas após a mudança
- linguagem adotada
- escopo exato da exceção
- data de reavaliação

Exceções não documentadas são consideradas dívida técnica.

---

## 6. Escrita de código

- código deve ser legível antes de ser otimizado
- métodos pequenos e com responsabilidade clara
- nomes explícitos são preferíveis a comentários explicativos
- evite abstração prematura
- clareza vence elegância

Código difícil de entender é bug em potencial.

---

## 7. Revisão de código

Revisão de código existe para melhorar qualidade, não para impor estilo pessoal.

### Bloqueia merge

- bug funcional
- problema de segurança
- violação clara deste manual
- código impossível de manter

### Não bloqueia merge

- preferências pessoais
- estilo quando não há padrão definido
- micro otimizações sem impacto real

Comentários devem ser objetivos, respeitosos e técnicos.

---

## 8. Testes

Testes existem para reduzir risco, não para inflar métricas.

- teste o que pode quebrar
- priorize comportamento crítico
- evite testes frágeis
- não teste detalhe de implementação sem necessidade

Teste que falha sem indicar problema real é custo, não benefício.

---

## 9. Performance

- não otimize antes de medir
- não confunda lentidão com má arquitetura
- não sacrifique legibilidade sem ganho claro
- documente decisões de otimização relevantes

Performance é responsabilidade contínua, não fase final.

---

## 10. Código legado

Código legado é código que funciona e gera valor.

- proteja antes de mudar
- refatore em pequenos passos
- evite reescritas completas sem necessidade extrema
- aceite dívida técnica quando o custo de pagar for maior que o risco

Legado mal tratado vira risco operacional.

---

## 11. Produção e operação

Todo código em produção deve permitir diagnóstico.

- logs claros e úteis
- métricas mínimas definidas
- erros visíveis, não silenciosos
- comportamento previsível em falha

Se não dá para observar, não dá para operar.

---

## 12. Evolução do manual

Este manual é vivo.

- práticas podem ser ajustadas
- exceções podem virar padrão
- padrões podem ser removidos

Toda mudança deve ser baseada em aprendizado real e impacto observado.
