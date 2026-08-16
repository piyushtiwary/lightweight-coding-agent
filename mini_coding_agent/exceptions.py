# Domain-specific exception hierarchy for Mini Coding Agent.

class AgentError(Exception):
    """Base exception for all agent harness errors."""
    pass


class SecurityError(AgentError):
    """Raised when an operation violates workspace boundary or sandbox policies."""
    pass


class ToolValidationError(AgentError):
    """Raised when tool arguments fail schema validation."""
    pass


class ToolExecutionError(AgentError):
    """Raised when a tool fails during execution."""
    pass


class LLMError(AgentError):
    """Raised when an LLM provider fails to respond or returns an error."""
    pass


class LLMConnectionError(LLMError):
    """Raised when connection to an LLM provider fails."""
    pass


class LLMTimeoutError(LLMError):
    """Raised when an LLM request exceeds the allotted timeout."""
    pass


class LLMResponseError(LLMError):
    """Raised when an LLM returns an invalid or malformed response."""
    pass