"""
Memory Manager Scripts Package
"""

from .memory_ops import (
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
