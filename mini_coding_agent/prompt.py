"""System prompt construction and KV-cache friendly prefix generation."""

from mini_coding_agent.workspace import WorkspaceContext


class PromptBuilder:
    """Builds structured prompts with KV-cache optimized prefix placement."""

    SYSTEM_RULES = (
        "- Use tools instead of guessing about the workspace.",
        "- Return exactly one <tool>...</tool> or one <final>...</final>.",
        "- Tool calls must look like:",
        '  <tool>{"name":"tool_name","args":{...}}</tool>',
        "- For write_file and patch_file with multi-line text, prefer XML style:",
        '  <tool name="write_file" path="file.py"><content>...</content></tool>',
        "- Final answers must look like:",
        "  <final>your answer</final>",
        "- Never invent tool results.",
        "- Keep answers concise and concrete.",
        "- If the user asks you to create or update a specific file and the path is clear, "
        "use write_file or patch_file instead of repeatedly listing files.",
        "- Before writing tests for existing code, read the implementation first.",
        "- When writing tests, match the current implementation unless the user explicitly "
        "asked you to change the code.",
        "- New files should be complete and runnable, including obvious imports.",
        "- Do not repeat the same tool call with the same arguments if it did not help. "
        "Choose a different tool or return a final answer.",
        "- Required tool arguments must not be empty. Do not call read_file, write_file, "
        "patch_file, run_shell, or delegate with args={}.",
    )


    VALID_EXAMPLES = (
        '<tool>{"name":"list_files","args":{"path":"."}}</tool>',
        '<tool>{"name":"read_file","args":{"path":"README.md","start":1,"end":80}}</tool>',
        '<tool name="write_file" path="binary_search.py"><content>def binary_search(nums, target):\n    return -1\n</content></tool>',
        '<tool name="patch_file" path="binary_search.py"><old_text>return -1</old_text><new_text>return mid</new_text></tool>',
        '<tool>{"name":"run_shell","args":{"command":"pytest -q","timeout":20}}</tool>',
        "<final>Done.</final>",
    )


    @classmethod
    def build_prefix(cls, tools_schema_text: str, workspace: WorkspaceContext) -> str:
         """Construct the immutable prefix containing rules, tool schemas, and workspace facts."""

         rules_test = "Rules:\n" + "\n".join(cls.SYSTEM_RULES)
         examples_text = "Valid response examples:\n" + "\n".join(cls.VALID_EXAMPLES)
         tools_text = "Tools:\n" + tools_schema_text

         return "\n\n".join([
               "You are Mini-Coding-Agent, a focused coding assistant with tool execution capabilities.",
               rules_test,
               tools_text,
               examples_text,
               workspace.format_text(),
         ])


    @classmethod
    def assemble_full_prompt(cls, prefix: str, memory_text: str, transcript_text: str, current_request: str) -> str:
         """Assemble complete multi-section prompt for LLM consumption."""

         return "\n\n".join([
              prefix,
              memory_text,
              "Transcript:\n" + transcript_text,
              "Current user request:\n" + current_request
         ])
