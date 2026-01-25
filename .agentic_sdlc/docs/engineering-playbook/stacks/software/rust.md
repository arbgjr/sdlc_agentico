<!-- /engineering-playbook/stacks/software/rust.md -->

# Stack Software. Rust

Rust deve ser tratado como escolha especializada.
Ele gera custo de adoção e exige justificativa objetiva.

## Status

Não é padrão geral.
É candidato para exceções de performance ou segurança, com isolamento obrigatório.

## Quando usar

- componentes onde performance é requisito e gargalo foi medido
- bibliotecas críticas com alto risco de falha
- parsers, processamento binário, criptografia, compressão
- componentes de borda com necessidade de baixo consumo de memória
- cenários onde segurança de memória é fator relevante

## Quando não usar

- por preferência pessoal
- como primeira escolha para produto comum
- quando otimização de algoritmo e arquitetura ainda não foi feita
- quando o time não tem capacidade de manter

## Regras de adoção

Para adotar Rust em um sistema cuja stack padrão é outra:

1. evidência de gargalo
2. melhoria esperada relevante, não marginal
3. isolamento em fronteira clara
4. contrato estável e testado
5. build e deploy definidos e automatizados
6. observabilidade do componente

## Integração com stack padrão

- expor interface clara, por exemplo via serviço separado ou biblioteca com bindings
- reduzir acoplamento
- permitir substituição futura

## Segurança e supply chain

- dependências precisam ser auditadas
- versões precisam ser fixadas
- pipeline deve garantir reprodutibilidade

## Exceções

Se Rust virar recorrente no mesmo tipo de problema:
- consolidar como padrão específico
- registrar decisão e atualizar stack

