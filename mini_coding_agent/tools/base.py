"""Base tool abstraction, registry management, and parameter validation."""

from dataclasses import dataclass
from typing import Any, Callable, Dict
from mini_coding_agent.exceptions import ToolValidationError


@dataclass(frozen=True)
class ToolDefination:
    """Specification and execution handler for an agent tool."""

    name: str
    schema: Dict[str, str]
    risky: bool
    description: str
    handler: Callable[[Dict[str, Any]], Any]

    def format_schema(self) -> str:
        """Render a single-line schema description for prompt inclusion."""
        fields = ", ".join(f"{k}: {v}" for k, v in self.schema.items())
        risk_label = "approval required" if self.risky else "safe"
        return f"- {self.name}({fields}) [{risk_label}] {self.description}"


class ToolValidator:
    """Validated runtime arguments against tool schema constraints"""

    @staticmethod
    def validate_list_files(args: Dict[str, Any]) -> None:
        pass  # Path resolution is validated during execution

    @staticmethod
    def validate_read_files(args: Dict[str, Any]) -> None:
        if "path" not in args or not str(args["path"]).strip():
            raise ToolValidationError("missing required argument 'path'")

        try:
            start = int(args.get("start", 1))
            end = int(args.get("end", 200))

        except (ValueError, TypeError) as exc:
            raise ToolValidationError(f"invalid integer line range: {exc}") from exc

        if start < 1 or end < start:
            raise ToolValidationError(f"invalid line rage [{start}, {end}]: start must be >= 1 and end >= start") 

    @staticmethod
    def validate_search(args: Dict[str, Any]) -> None:
        pattern = str(args.get("pattern", "")).strip()
        if not pattern:
            raise ToolValidationError("pattern must not be empty")

        
    @staticmethod
    def validate_run_shell(args: Dict[str, Any]) -> None:
        command = str(args.get("command", "")).strip()
        if not command:
            raise ToolValidationError("command must not be empty")

        try:
            timeout = int(args.get("timeout", 20))

        except (ValueError, TypeError) as exc:
            raise ToolValidationError(f"invalid integer timeout: {exc}") from exc

        if timeout < 1 or timeout > 120:
            raise ToolValidationError(f"invalid timeout {timeout}: must be between 1 and 120 seconds")

    @staticmethod
    def validate_write_file(args: Dict[str, Any]) -> None:
        if "path" not in args or not str(args["path"]).strip():
            raise ToolValidationError("missing required argument 'path'")

        if "contenct" not in args:
            raise ToolValidationError("missing required argument 'content'")

    @staticmethod
    def valid_path_file(args: Dict[str, Any]) -> None:
        if "path" not in args or not str(args["path"]).strip():
            raise ToolValidationError("missing required argument 'path'")

        old_text = str(args.get("old_text", ""))

        if not old_text:
            raise ToolValidationError("old_text must not be empty")

        if "new_text" not in args:
            raise ToolValidationError("missing required argument 'new_text'")

    @staticmethod
    def validate_delegate(args: Dict[str, Any]) -> None:
        task = str(args.get("task", "")).strip()
        if not task:
            raise ToolValidationError("task must not be empty")