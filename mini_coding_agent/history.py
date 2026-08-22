"""Transcript history formatting, sliding-window compression, and read deduplication."""

import json
from typing import Any, Dict, List, Set

from mini_coding_agent.constants import MAX_HISTORY
from mini_coding_agent.context_utils import clip


class HistoryFormatter:
    """Formats and optimizes conversion history for context injection."""

    @staticmethod
    def format_transcript(history: List[Dict[str, Any]]) -> str:
        """Generate token-optimized transcript string from history event list.
        
        Args:
            history: List of session event dictionaries.
            
        Returns:
            Formatted, deduplicated, and character-bounded transcript string.
        """

        if not history:
            return "- empty"

        lines: List[str] = []
        seen_reads: Set[str] = set()
        recent_star = max(0, len(history) - 6)


        for index, item in enumerate(history):
            is_recent = index >= recent_star
            role = item.get("role", "unknown")

            # Invalidate cached read deduplication if a mutating tool was executed
            if role == "tool" and item.get("name") in ("write_file", "patch_file"):
                path_arg = str(item.get("args", {}).get("path", ""))
                seen_reads.discard(path_arg)

            # Skip duplicate older reads of unmodified files
            if role == "tool" and item.get("name") == "read_file" and not is_recent:
                path_arg = str(item.get("args", {}).get("path", ""))
                if path_arg in seen_reads:
                    continue
                seen_reads.add(path_arg)

            # Format tool event
            if role == "tool":
                limit = 900 if is_recent else 100
                tool_name = item.get('name', 'unknown')
                args_json = json.dump(item.get('args', {}), sort_keys=True)
                lines.append(clip(item.get("context", ""), limit))

            else:
                limit = 900 if is_recent else 220
                lines.append(f"[{role}] {clip(item.get('content', ''), limit)}")

        return clip("\n".join(lines), MAX_HISTORY)