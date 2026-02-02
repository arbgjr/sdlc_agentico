#!/usr/bin/env python3
"""
Script: Report SDLC Bug

Reports bugs from SDLC Agêntico to the framework owner (arbgjr) by creating
GitHub issues in the arbgjr/sdlc_agentico repository.

Usage:
    python3 report_sdlc_bug.py classified_errors.json
"""

import sys
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Tuple, Optional

# Add lib path for imports
SCRIPT_DIR = Path(__file__).resolve().parent
LIB_DIR = SCRIPT_DIR.parent.parent.parent / "lib" / "python"
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

        def warning(self, msg, **kwargs):
            self.logger.warning(f"{msg} {kwargs}")

        def error(self, msg, **kwargs):
            self.logger.error(f"{msg} {kwargs}")

    def get_logger(name, skill=None, phase=None):
        return FallbackLogger(name)


class BugReporter:
    """Reports SDLC bugs to GitHub."""

    REPO_OWNER = "arbgjr"
    REPO_NAME = "sdlc_agentico"

    def __init__(self, classified_json_path: str):
        self.logger = get_logger(__name__, skill="session-analyzer")
        self.repo_root = Path.cwd()
        self.classified_json_path = Path(classified_json_path)

    def run_command(
        self, cmd: list[str], capture_output: bool = True
    ) -> Tuple[int, str, str]:
        """
        Run command and return (returncode, stdout, stderr).

        Args:
            cmd: Command to run
            capture_output: Whether to capture output

        Returns:
            Tuple of (returncode, stdout, stderr)
        """
        try:
            result = subprocess.run(
                cmd,
                capture_output=capture_output,
                text=True,
                check=False,
            )
            return result.returncode, result.stdout.strip(), result.stderr.strip()
        except Exception as e:
            self.logger.error(f"Command failed: {' '.join(cmd)}", extra={"error": str(e)})
            return 1, "", str(e)

    def get_git_info(self) -> dict:
        """
        Get current git repository information.

        Returns:
            Dictionary with origin, branch, commit
        """
        info = {
            "origin": "unknown",
            "branch": "unknown",
            "commit": "unknown",
        }

        # Get remote origin
        code, stdout, _ = self.run_command(["git", "remote", "get-url", "origin"])
        if code == 0:
            info["origin"] = stdout

        # Get current branch
        code, stdout, _ = self.run_command(["git", "branch", "--show-current"])
        if code == 0:
            info["branch"] = stdout

        # Get commit hash
        code, stdout, _ = self.run_command(["git", "rev-parse", "--short", "HEAD"])
        if code == 0:
            info["commit"] = stdout

        return info

    def load_classified_errors(self) -> Optional[dict]:
        """
        Load classified errors JSON file.

        Returns:
            Dictionary with classified errors or None if error
        """
        if not self.classified_json_path.exists():
            self.logger.error(
                f"✗ Arquivo de erros não encontrado: {self.classified_json_path}"
            )
            return None

        try:
            with open(self.classified_json_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(
                f"Erro ao ler arquivo JSON: {str(e)}",
                extra={"file": str(self.classified_json_path), "error": str(e)}
            )
            return None

    def generate_issue_body(self, bugs: list, git_info: dict) -> str:
        """
        Generate GitHub issue body from bugs.

        Args:
            bugs: List of bug dictionaries
            git_info: Git repository information

        Returns:
            Markdown issue body
        """
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        # Build bug details
        bug_details = []
        for bug in bugs:
            # Generate unique ID from timestamp
            bug_id = str(bug.get("timestamp", ""))[-6:]

            classification = bug.get("classification", {})
            confidence = classification.get("confidence", 0) * 100

            detail = f"""#### Bug #{bug_id}

**Classificação**: {classification.get("classification", "unknown")} (confidence: {int(confidence)}%)
**Skill**: {bug.get("skill", "unknown")}
**Script**: {bug.get("script", "N/A")}
**Timestamp**: {bug.get("timestamp", "unknown")}

**Mensagem**:
```
{bug.get("message", "No message")}
```

**Razão**:
{classification.get("reason", "No reason provided")}

---
"""
            bug_details.append(detail)

        return f"""## 🐛 Bugs Detectados Automaticamente

**Total de bugs**: {len(bugs)}
**Reportado em**: {timestamp}
**Projeto**: {git_info["origin"]}
**Branch**: {git_info["branch"]}
**Commit**: {git_info["commit"]}

---

### Detalhes dos Bugs

{''.join(bug_details)}

### Contexto Adicional

Esses bugs foram detectados automaticamente durante a execução do SDLC Agêntico.
A análise de erros do Loki identificou esses problemas como bugs do framework.

**Ação Recomendada**:
1. Investigar os erros listados acima
2. Corrigir os bugs no framework
3. Criar hotfix se necessário
4. Atualizar testes para prevenir regressão
"""

    def create_github_issue(self, title: str, body: str) -> bool:
        """
        Create GitHub issue using gh CLI.

        Args:
            title: Issue title
            body: Issue body (markdown)

        Returns:
            True if successful
        """
        repo = f"{self.REPO_OWNER}/{self.REPO_NAME}"

        print(f"Criando GitHub issue em {repo}...")

        cmd = [
            "gh",
            "issue",
            "create",
            "--repo",
            repo,
            "--title",
            title,
            "--body",
            body,
            "--label",
            "bug,auto-report",
        ]

        code, stdout, stderr = self.run_command(cmd)

        if code == 0:
            print(f"✓ Issue criado com sucesso no repositório {repo}")
            if stdout:
                print(f"  {stdout}")
            return True
        else:
            self.logger.warning(
                "Falha ao criar GitHub issue",
                extra={"code": code, "stderr": stderr}
            )
            return False

    def save_local_report(self, title: str, body: str) -> bool:
        """
        Save bug report locally if GitHub issue creation fails.

        Args:
            title: Report title
            body: Report body

        Returns:
            True if successful
        """
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        report_file = self.repo_root / ".agentic_sdlc" / "bug-reports" / f"report-{timestamp}.md"

        # Create directory if needed
        report_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(report_file, "w", encoding="utf-8") as f:
                f.write(f"# {title}\n\n")
                f.write(body)
                f.write("\n\n---\n\n")
                f.write("**NOTA**: Este report foi salvo localmente porque não foi possível criar GitHub issue.\n")
                f.write(f"Para reportar manualmente, acesse: https://github.com/{self.REPO_OWNER}/{self.REPO_NAME}/issues/new\n")

            print(f"   Report salvo em: {report_file}")
            print(f"   Por favor, reporte manualmente: https://github.com/{self.REPO_OWNER}/{self.REPO_NAME}/issues/new")
            return True

        except Exception as e:
            self.logger.error(
                f"Erro ao salvar report local: {str(e)}",
                extra={"file": str(report_file), "error": str(e)}
            )
            return False

    def execute(self) -> int:
        """
        Execute bug reporting.

        Returns:
            0 on success, 1 on failure
        """
        # Load classified errors
        data = self.load_classified_errors()
        if data is None:
            return 1

        # Get bug count
        summary = data.get("summary", {})
        bugs = data.get("sdlc_bugs", [])
        bug_count = summary.get("sdlc_bugs", len(bugs))

        if bug_count == 0:
            print("✓ Nenhum bug do SDLC para reportar")
            return 0

        print(f"📤 Reportando {bug_count} bugs do SDLC Agêntico ao owner...")

        # Get git info
        git_info = self.get_git_info()

        # Generate issue content
        title = f"[Auto-Report] {bug_count} bugs detectados na execução"
        body = self.generate_issue_body(bugs, git_info)

        # Try to create GitHub issue
        if not self.create_github_issue(title, body):
            print("⚠ Falha ao criar issue. Salvando report local...")
            self.save_local_report(title, body)

        return 0


def main() -> int:
    """
    Main entry point for report_sdlc_bug script.

    Usage:
        python3 report_sdlc_bug.py classified_errors.json

    Returns:
        Exit code (0 on success, 1 on failure)
    """
    if len(sys.argv) < 2:
        print("✗ Uso: python3 report_sdlc_bug.py classified_errors.json", file=sys.stderr)
        return 1

    classified_json = sys.argv[1]

    reporter = BugReporter(classified_json)

    try:
        return reporter.execute()
    except Exception as e:
        reporter.logger.error(
            f"Bug reporting failed: {str(e)}",
            extra={"error": str(e), "type": type(e).__name__}
        )
        print(f"\n❌ Error: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
