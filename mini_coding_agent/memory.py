"""Distilled working memory management and LRU collection tracking."""

from typing import Any, Dict, List
from mini_coding_agent.context_utils import clip


class MemoryManager:
    """Manages distilled task state, touched files, and progress notes."""

    @staticmethod
    def remember(bucket: List[str], item: str, limit: int) -> None:
        """Insert item into bucket with deduplication and LRU eviction.
        
        Args:
            bucket: Target list to mutate.
            item: String item to add.
            limit: Maximum allowed items in bucket.
        """

        if not item:
            return

        if item in bucket:
            bucket.remove(item)

        bucket.append(item)
        del bucket[: -limit]


    @classmethod
    def record_tool_result(
        cls,
        memory: Dict[str, Any],
        tool_name: str,
        args: Dict[str, Any],
        result: str,
    ) -> None:
        """Update working memory following tool execution."""

        path = args.get("path")
        if tool_name in {"read_file", "write_file", "patch_file"} and path:
            cls.remember(memory["files"], str(path), limit=8)

        # Distill single-line summary note
        single_line_res = str(result).replace("\n", " ")
        note = f"{tool_name}: {clip(single_line_res), 220}"
        cls.remember(memory["notes"], note, limit=5)


    @staticmethod
    def format_text(memory: Dict[str, Any]) -> str:
        """Format working memory for inclusion in prompt."""
        task_str = memory.get("task") or "-"
        files_list = memory.get("files", [])
        files_str = ", ".join(files_list) if files_list else "-"
        notes_list = memory.get("notes", [])
        notes_str = "\n".join(f"- {n}" for n in notes_list) if notes_list else "- none"

        return "\n".join([
            "Memory:",
            f"- task: {task_str}",
            f"- files: {files_str}",
            "- notes:",
            notes_str,
        ])