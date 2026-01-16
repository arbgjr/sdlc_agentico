#!/usr/bin/env python3
"""
Wrapper/alias para memory_ops.py
Mantido para compatibilidade com codigo que referencia memory_store.py
"""

import sys
from pathlib import Path

# Add scripts directory to path
scripts_dir = Path(__file__).parent
sys.path.insert(0, str(scripts_dir))

# Import all from memory_ops
from memory_ops import (
    ensure_directories,
    get_project_dir,
    save_decision,
    load_decision,
    search_decisions,
    save_learning,
    search_learnings,
    get_project_manifest,
    update_project_manifest,
    AGENTIC_SDLC_DIR,
    LEGACY_MEMORY_DIR
)

# Re-export all functions
__all__ = [
    'ensure_directories',
    'get_project_dir',
    'save_decision',
    'load_decision',
    'search_decisions',
    'save_learning',
    'search_learnings',
    'get_project_manifest',
    'update_project_manifest',
    'AGENTIC_SDLC_DIR',
    'LEGACY_MEMORY_DIR'
]
