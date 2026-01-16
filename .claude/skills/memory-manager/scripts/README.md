# Memory Manager Scripts

Scripts para gerenciar a memória persistente do SDLC Agêntico.

## Arquivos

### memory_ops.py
Script principal com todas as operações de memória:
- `save_decision()` - Salvar ADRs
- `load_decision()` - Carregar ADRs
- `search_decisions()` - Buscar decisões
- `save_learning()` - Salvar learnings
- `search_learnings()` - Buscar learnings
- `get_project_manifest()` - Obter manifest do projeto
- `update_project_manifest()` - Atualizar manifest

### memory_store.py
Wrapper/alias para `memory_ops.py` para compatibilidade com código que referencia `memory_store.py`.

### __init__.py
Package init que permite import do módulo como pacote Python.

## Uso

```python
import sys
sys.path.insert(0, '.claude/skills/memory-manager/scripts')

from memory_ops import save_decision, load_decision

# Salvar decisão
decision_id = save_decision(
    project_id="meu-projeto",
    decision_type="architecture",
    title="Usar PostgreSQL como database",
    context="Precisamos de ACID compliance",
    decision="PostgreSQL 15 com replicação",
    consequences=["Requer DBA", "Custo operacional mais alto"],
    phase=3
)

# Carregar decisão
adr = load_decision("meu-projeto", decision_id)
print(adr['title'])
```

## Estrutura de Armazenamento

Versão 1.2.0+ usa `.agentic_sdlc/` como diretório principal:

```
.agentic_sdlc/
├── projects/
│   └── {project-id}/
│       ├── manifest.yml
│       ├── decisions/
│       │   ├── adr-001.yml
│       │   └── adr-002.yml
│       ├── learnings/
│       │   └── learning-001.yml
│       └── phases/
└── corpus/
    ├── decisions/
    └── learnings/
```

## Testes

Execute `memory_ops.py` diretamente para testes básicos:

```bash
python3 .claude/skills/memory-manager/scripts/memory_ops.py
```

Saída esperada:
```
Diretorios criados com sucesso
Decisao salva: ADR-001
Decisao carregada: Teste de decisao
```
