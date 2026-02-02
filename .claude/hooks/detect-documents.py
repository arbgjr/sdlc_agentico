#!/usr/bin/env python3
"""
Hook: Detect Documents

Detects PDF/XLSX/DOCX files in project and suggests document-processor skill.
Triggered on UserPromptSubmit.
"""

import sys
from typing import List
from pathlib import Path

# Add lib path for imports
SCRIPT_DIR = Path(__file__).resolve().parent
LIB_DIR = SCRIPT_DIR.parent / "lib" / "python"
sys.path.insert(0, str(LIB_DIR))

try:
    from sdlc_logging import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)

    class FallbackLogger:
        def __init__(self, name):
            self.logger = logging.getLogger(name)

        def info(self, msg, **kwargs):
            self.logger.info(f"{msg} {kwargs}")

        def debug(self, msg, **kwargs):
            self.logger.debug(f"{msg} {kwargs}")

    def get_logger(name, skill=None, phase=None):
        return FallbackLogger(name)


class DocumentDetector:
    """Detects office documents in project."""

    # Document file extensions to look for
    DOCUMENT_EXTENSIONS = [".pdf", ".xlsx", ".xls", ".docx", ".doc"]

    def __init__(self):
        self.logger = get_logger(__name__, skill="document-processor", phase=0)
        self.repo_root = Path.cwd()

    def find_documents(self) -> List[Path]:
        """
        Find document files in project.

        Returns:
            List of document file paths
        """
        documents = []

        # Search in common locations (max depth 3)
        for ext in self.DOCUMENT_EXTENSIONS:
            pattern = f"*{ext}"
            for depth in range(1, 4):
                search_pattern = "/".join(["*"] * depth) + f"/{pattern}"
                documents.extend(self.repo_root.glob(search_pattern))

        # Search in .agentic_sdlc/references
        references_dir = self.repo_root / ".agentic_sdlc" / "references"
        if references_dir.exists():
            for ext in self.DOCUMENT_EXTENSIONS:
                pattern = f"**/*{ext}"
                documents.extend(references_dir.glob(pattern))

        # Filter to only files (not directories)
        documents = [d for d in documents if d.is_file()]

        # Remove duplicates and sort
        documents = sorted(set(documents))

        return documents

    def execute(self) -> int:
        """
        Execute document detection.

        Returns:
            0 always (never block)
        """
        self.logger.debug("Scanning for documents")

        # Find documents
        documents = self.find_documents()

        if documents:
            self.logger.info(
                "Documents detected",
                extra={"count": len(documents)}
            )

            # Output environment variables
            print("DOCUMENTS_DETECTED=true")
            print(f"DOCUMENT_COUNT={len(documents)}")
            print("DOCUMENTS_HINT=Use /doc-extract to process documents")

            # List first 5 documents
            for idx, doc in enumerate(documents[:5]):
                rel_path = doc.relative_to(self.repo_root)
                self.logger.debug(
                    "Document found",
                    extra={"path": str(rel_path)}
                )
                print(f"DOCUMENT_{idx}={rel_path}")
        else:
            self.logger.debug("No documents found")

        return 0


def main() -> int:
    """
    Main entry point for detect-documents hook.

    Returns:
        Exit code (0 always)
    """
    detector = DocumentDetector()

    try:
        return detector.execute()
    except Exception as e:
        detector.logger.debug(
            f"Document detection failed: {str(e)}",
            extra={"error": str(e), "type": type(e).__name__}
        )
        # Don't block on errors
        return 0


if __name__ == "__main__":
    sys.exit(main())
