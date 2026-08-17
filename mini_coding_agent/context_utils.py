# Context budgeting, string trimming, and formatting utilities.

from datetime import datetime, timezone

from mini_coding_agent.constants import MAX_TOOL_OUTPUT


def utc_now() ->str:
    """Return the current UTC timestamp formatted as ISO-8601(YY-MM-DD) string"""
    
    return datetime.now(timezone.utc).isoformat()


def clip(text: object, limit: int = MAX_TOOL_OUTPUT) -> str:
    """Truncate text to limit characters, appending a descriptor of omitted volume."""

    text_str = str(text)
    if len(text_str) <= limit:
        return text_str

    omitted = len(text_str) - limit
    return  text_str[: limit] + f"...[truncated {omitted} chars]"


def middle(text: object, limit: int) -> str:
    """Condense a string by preserving prefix and suffix with an ellipsis in the middle.
        Newlines are converted to spaces to guarantee single-line fit for UI cells.
    """

    clean_text = str(text).replace("\n", " ")
    if len(clean_text) < limit:
        return clean_text

# The ellipsis ... itself requires 3 characters
    if limit <= 3: 
        return clean_text[: limit]

    left = (limit - 3) // 2
    right = limit - 3 - left

    return clean_text[:left] + "..." + clean_text[-right:]