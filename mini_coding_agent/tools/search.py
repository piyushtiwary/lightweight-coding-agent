"""Workspace search using ripgrep with pure-Python fallback."""

from pathlib import Path
import shutil
import subprocess
from typing import Dict, Any, List

from mini_coding_agent.constants import IGNORED_PATH_NAMES
from mini_coding_agent.security import PathValidator
from mini_coding_agent.tools.base import ToolValidator


class SearchTool:
    """Executes workspace text searches via rg subprocess or recursive Python traversal."""


    def __init__(self, path_validator: PathValidator, repo_root: Path):
        self.validator = path_validator
        self.root = repo_root

    def search(self, args: Dict[str, Any]) -> str:
        """Search workspace file for a text pattern"""

        ToolValidator.validate_search(args)
        pattern = str(args["pattern"]).strip()
        search_path = self.validator.resolve_safe_path(args.get("path", "."))

        # Check for system ripgrep binary
        if shutil.which("rg"):
            result = subprocess.run(
                ["rg", "-n", "--smart-case", "--max-count", "200", pattern, str(search_path)],
                cwd=self.root,
                capture_output=True,
                text=True
            )

            output = result.stdout.strip() or result.stderr.strip()
            return output if output else "(no matches)"

        #Fallback
        matches: List[str] = []
        if search_path.is_file():
            target_file = [search_path]

        else:
            target_file = [
                p for p in search_path.rglob("*")
                if p.is_file() and not any(part in IGNORED_PATH_NAMES for part in p.relative_to(self.root).parts)
            ]

        for file_path in target_file:
            try:
                content = file_path.read_text(encoding='utf-8', errors='replace')

            except OSError:
                continue

            for line_no, line in enumerate(content.splitlines(), start=1):
                if pattern.lower() in line.lower():
                    rel_path = file_path.relative_to(self.root)
                    matches.append(f"{rel_path}:{line_no}:{line}")
                    if len(matches) >= 200:
                        return "\n".join(matches)

        return "\n".join(matches) if matches else "(no matches)"