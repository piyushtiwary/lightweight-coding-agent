"""Security policy enforcement and interactive user approval gates."""

import json
from typing import Any, Dict, Literal


ApprovalPolicy = Literal["ask", "auto", "never"]


class ApprovalGate:
    """Gates risky tool actions behind user approval or automated policies."""

    def __init__(self, policy: ApprovalPolicy = "ask", read_only: bool = False):

        self.policy: ApprovalPolicy = policy
        self.read_only: bool = read_only


    def is_approved(self, tool_name: str, args: Dict[str, Any]) -> bool:
        """Determine whether the specified tool execution is authorized.
        
        Args:
            tool_name: Name of tool being invoked.
            args: Parameter dictionary.
            
        Returns:
            True if authorized, False otherwise.
        """

        if self.read_only:
            return False

        if self.policy == "auto":
            return True

        if self.policy == "never":
            return False


         # Interactive approval prompt for 'ask' policy
        args_preview = json.dump(args, ensure_ascii=False)
        try:
            prompt_str = f"approve {tool_name} {args_preview}? [y/N] "
            user_response = input(prompt_str)

        except (EOFError, KeyboardInterrupt):
            return False


        return user_response.strip().lower() in {"y", "yes"}