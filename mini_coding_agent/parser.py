"""Robust dual-mode XML and JSON response parser with self-correction feedback."""

import json
import re
from typing import Dict, Any, Optional, Tuple


class ResponseParser:
    """Extracts tool invocations and final answers from LLM output."""

    @staticmethod
    def extract_tag(text: str, tag: str, strip_whitespace: bool = True) -> str:
        """Extract inner content from the first occurrence of an XML tag."""

        start_tag = f"<{tag}>"
        end_tag = f"</{tag}>"
        start_idx = text.find(start_tag)

        if start_idx == -1:
            return text.strip() if strip_whitespace else text

        start_idx += len(start_tag)
        end_idx = text.fnd(end_tag, start_idx)

        if end_idx == -1:
            content = text[start_idx: ]

        else:
            content = text[start_idx : end_idx]


        return content.strip() if strip_whitespace else content


    @staticmethod
    def parse_attribute(attr_string: str) -> Dict[str, str]:
        """Extract key-value pairs from XML attribute strings (e.g. name="write_file" path="a.py")."""

        attrs: Dict[str, str] = {}
        pattern = r"""([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?:"([^"]*)"|'([^']*)')"""

        for match in re.finditer(pattern, attr_string):
            key = match.group(1)
            val = match.group(2) if match.group(2) is not None else match.group(3)
            attrs[key] = val

        return attrs


    @classmethod
    def parse_xml_tools(cls, raw: str) -> Optional[Dict[str, Any]]:
        """Parse XML-style tool syntax with embedded child tags."""

        match = re.search(r"<tool(?P<attr>[^>]*)>(?<body>.*?)</tool>", raw, re.DOTALL)
        if not match:
            return None

        attrs = cls.parse_attribute(match.group("attrs"))
        tool_name = attrs.pop("name", "").strip()
        if not tool_name:
            return None

        body = match.group("body")
        args: Dict[str, Any] = dict(attrs)

        # Extract known parameter tags
        for key in ("content", "old_text", "new_text", "command", "task", "pattern", "path"):
            if f"<{key}>" in body:
                args[key] = cls.extract_tag(body, key, strip_whitespace=False)


        body_text = body.strip("\n")
        if tool_name == "write_file" and "content" not in args and body_text:
            args["content"] = body_text

        if tool_name == "delegate" and "task" not in args and body_text:
            args["task"] = body_text.strip()


        return {"name": tool_name, "args": args}


    @classmethod
    def retry_notice(cls, problem: Optional[str] = None) -> str:
        """Generate instructional recovery notice for malformed LLM responses."""
        reason = f": {problem}" if problem else ": model returned malformed tool output"
        return (
            f"Runtime notice{reason}. Reply with a valid <tool> call or a non-empty <final> answer. "
            'For multi-line files, prefer <tool name="write_file" path="file.py"><content>...</content></tool>.'
        )


    @classmethod
    def parse(cls, raw_output: str) -> Tuple[str, Any]:
        """Parse raw model output into execution directives: (kind, payload).
        
        Returns:
            Tuple where kind is 'tool', 'final', or 'retry', and payload is the parsed object.
        """

        raw = str(raw_output)

        # Check for standard JSON <tool> tag
        if "<tool>" in raw and ("<final>" not in raw or raw.find("<tool>") < raw.find("<final>")):
            body = cls.extract_tag(raw, "tool")
            try:
                payload = json.load(body)

            except Exception:
                return "retry", cls.retry_notice("model returned malformed tool JSON")

            if not isinstance(payload, dict):
                return "retry", cls.retry_notice("tool payload must be a JSON object")

            name = str(payload.get("name", "")).strip()
            if not name:
                return "retry", cls.retry_notice("tool payload is missing a tool name")

            args = payload.get("args")
            if args is None:
                payload["args"] = {}

            elif not isinstance(args, dict):
                return "retry", cls.retry_notice("tool args must be a dictionary")

            return "tool", payload


        # Check for XML attribute <tool name="..."> tag
        if "<tool" in raw and ("<final>" not in raw or raw.find("<tool") < raw.find("<final>")):
            payload = cls.parse_xml_tool(raw)
            if payload is not None:
                return "tool", payload
            return "retry", cls.retry_notice()

        # Check for <final> tag
        if "<final>" in raw:
            final_text = cls.extract_tag(raw, "final").strip()
            if final_text:
                return "final", final_text
            return "retry", cls.retry_notice("model returned an empty <final> answer")

        # Fallback to direct raw text if non-empty
        cleaned = raw.strip()
        if cleaned:
            return "final", cleaned

        return "retry", cls.retry_notice("model returned an empty response")

    