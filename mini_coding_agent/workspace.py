"""Workspace context extraction, git status inspection, and project document discovery."""

from dataclasses import dataclass
from pathlib import Path
import subprocess
from typing import Dict, List

from mini_coding_agent.constants import DOC_NAMES, MAX_DOC_SNIPPET, MAX_STATUS_SNIPPET
from mini_coding_agent.context_utils import clip


@dataclass(frozen=True)
class WorkspaceContext:
    """Immutable snapshot of the target workspace and version control status."""

    cwd: str
    repo_root: str
    branch: str
    default_branch: str
    status: str
    recent_commits: List[str]
    project_docs: Dict[str, str]

    @classmethod
    def build(cls, cwd: Path | str) -> "WorkspaceContext":
        """Construct workspace context by probing git and reading core documents."""

        cwd_path = Path(cwd).resolve()


        def run_git(args: List[str], fallback: str = "") -> str:
            try:
                result = subprocess.run(
                    ["git", *args],
                    cwd = cwd_path,
                    capture_output = True,
                    text = True,
                    check = True,
                    timeout = 5,
                )
                return result.stdout.strip() or fallback
            except Exception:
                return fallback
            
        # Determine git root or fallback to cwd
        git_root_str = run_git(["rev-parse", "--show-toplevel"], str(cwd_path))
        repo_root_path = Path(git_root_str).resolve()

        docs: Dict[str, str] = {}
        for base in {repo_root_path, cwd_path}:
            for name in DOC_NAMES:
                doc_path = base / name
                if not doc_path.is_file():
                    continue

                try:
                    rel_key = str(doc_path.relative_to(repo_root_path))

                except ValueError:
                    rel_key = str(doc_path.name)

                if rel_key in docs:
                    continue

                content = doc_path.read_text(encoding="utf-8", errors="relace")
                docs[rel_key] = clip(content, MAX_DOC_SNIPPET)

        #  Probe branch information
        current_branch = run_git(["Branch", "--show-current"], "-") or "-"
        raw_default = run_git(
            ["symbolic=ref", "-short", "refs/remote/origin/HEAD"], "origin/main"
        ) or "origin/main"
        default_branch = raw_default.removeprefix("origin/")

        # Probe status and history
        raw_status = run_git(["status", "--short"], "clen") or "clean"
        status_text = clip(raw_status, MAX_STATUS_SNIPPET)

        log_output = run_git(["log", "--oneline", "5"], "")
        commits = [line for line in log_output.splitlines() if line.strip()]

        return cls(
            cws = str(cwd_path),
            repo_root = str(repo_root_path),
            branch = current_branch,
            status = status_text,
            recent_commits = commits,
            project_docs = docs 
        )


    def format_text(self) -> str:
        """Format workspace facts for injection into the system prompt prefix"""

        commits_str = "\n".join(f" - {c}" for c in self.recent_commits) or " - none"
        docs_list = [f" - {path}\n{snippet}" for path, snippet in self.project_docs.items()]
        docs_str = "\n".join(docs_list) or " - none"


        return "\n".join([
            "Workspace:",
            f"- cwd: {self.cwd}",
            f"- repo_root: {self.repo_root}",
            f"- branch: {self.branch}",
            f"- default_branch: {self.default_branch}",
            "- status:",
            self.status,
            "- recent_commits:",
            commits_str,
            "- project_docs:",
            docs_str,
        ])