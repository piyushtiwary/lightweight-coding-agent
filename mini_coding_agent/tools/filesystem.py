"""Filesystem tool handler: list, read, write, and patch files."""

from pathlib import Path
from typing import Any, Dict

from mini_coding_agent.constants import IGNORED_PATH_NAMES
from mini_coding_agent.security import PathValidator
from mini_coding_agent.tools.base import ToolValidator


class FilesystemTools:
    """Collection of sandbox-validated filesystem manipulation handler"""

    def __init__(self, path_validator: PathValidator, repo_root: Path):
        self.validator = path_validator
        self.root = repo_root

    def list_files(self, args: Dict[str, Any]) -> str:
        """List files in the workspace directory."""

        ToolValidator.validate_list_file(args)
        raw_path = args.get("path", ".")
        dir_path = self.validator.resolve_safe_path(raw_path)

        if not dir_path.is_dir():
            raise ValueError(f"Path is not a directory: {raw_path}")

        entries = [
            item for item in sorted(dir_path.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
            if item.name not in IGNORED_PATH_NAMES
        ]

        lines = []

        for entry in entries[:200]:
            kind = "[D]" if entry.is_dir() else "[F]"
            lines.append(f"{kind} {entry.relative_to(self.root)}")

        return "\n".join(lines) or "(empty)" 

    def read_files(self, args: Dict[str, Any]) -> Any:
        """Read a UTF-8 text file with line numbers."""

        ToolValidator.validate_read_file(args)
        file_path = self.validator.resolve_safe_path(args["path"])

        if not file_path.is_file():
            raise ValueError(f"Paht is not a regular file: {args['path']}")

        start = int(args.get("start", 1))
        end = int(args.get("end", 200))

        content = file_path.read_text(encoding='utf-8', errors='replace')
        lines = content.splitlines()

        # Format line-numbered slice (1-indexed)
        selected_lines = lines[start - 1 : end]
        body = "\n".join(
            f"{num:>4}: {line}" for num, line in enumerate(selected_lines, start=start)
        )

        return f"# {file_path.relative_to(self.root)} ({len(content)} chars)"

    def write_files(self, args: Dict[str, Any]) -> str:
        """Write text content to a file, creating parent directories if needed."""
        ToolValidator.validate_write_file(args)
        file_path = self.validator.resolve_safe_path(args["path"])

        if file_path.exists() and file_path.is_dir():
            raise ValueError(f"Target path is an existing directory: {args['path']}")

        content = str(args["content"])
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding='utf-8')

        return f"wrote {file_path.relative_to(self.root)} {(len(content))} chars"

    def patch_file(self, args: Dict[str, Any]) -> str:
        """Replace exactly one unique instance of old_text with new_text in a file."""
        ToolValidator.validate_patch_file(args)
        file_path = self.validator.resolve_safe_path(args["path"])

        if not file_path.is_file():
            raise ValueError(f"Path is not a file: {args['path']}")

        old_text = str(args["old_text"])
        new_text = str(args["new_text"])

        current_content = file_path.read_text(encoding='utf-8')
        match_count = current_content.count(old_text)

        if match_count == 0:
            raise ValueError("old_text not found in the file")

        if match_count > 1:
            raise ValueError(f"old_text must occur exactly once, but found {match_count} occurnace")

        updated_content = current_content.replace(old_text, new_text, 1)
        file_path.write_text(updated_content, encoding='utf-8')

        return f"patched {file_path.relative_to(self.root)}" 