# System-wide configuration constants and tuning parameters.

# Document targets searched for initial workspace context
DOC_NAME = ("AGENTS.md", "README.md", "pyproject.toml", "package.json", "Cargo.toml")


# Tool execution and prompt context budget limits
MAX_TOOL_OUTPUT = 4000
MAX_HISTORY = 12000
MAX_DOC_SNIPPET = 1200
MAX_STATUS_SNIPPET = 1500


#  File system ignore list during searches and listing
IGNORED_PATH_NAMES = frozenset({
    ".git",
    ".mini-coding-agent",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "venv",
    ".mypy_cache",
    "node_modules",
})


# Terminal UI Welcome Art
WELCOME_ART = (
    r"/\     /\\",
    r"{  `---'  }",
    r"{  O   O  }",
    r"~~>  V  <~~",
    r"\\  \|/  /",
    r"`-----'__",
)


# REPL Command Help Details
HELP_DETAILS = "\n".join([
    "Commands: ",
    "/help          Show this command reference.",
    "/memory        Display the distilled working memory (tasks, files, notes).",
    "/session       Print the absolute file path of the active session JSON.",
    "/reset         Clear transcript history and working memory of this session.",
    "/exit          Terminate the interactive session.",
    "/quit          Alias for /exit.",               
])