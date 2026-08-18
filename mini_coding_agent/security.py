"""Filesystem sandboxing, path canonicalization, and workspace boundary security."""

from pathlib import Path
from mini_coding_agent.exceptions import SecurityError


class PathValidator:
	"""Enforces workspace encapsulation against path escapes and symlink attacks."""

	def __init__(self, workspace_root: Path | str):
		self.root = Path(workspace_root).resolve()


	def is_within_root(self, target_path: Path) -> bool:
		"""Verify whether target_path resolves strictly within the workspace root.
        
        Handles both existing files and pending creations by probing up through
        existing ancestor directories.
        """

		probe = target_path.resolve()
		while not probe.exists() and probe.parent != probe:
			probe = probe.parent

		for candidate in (probe, *probe.parents):
			try:
				if candidate.samefile(self.root):
					return True

			except (OSError, ValueError):
				continue
		return False


	def resolve_safe_path(self, raw_path: Path | str) -> Path:
		"""Resolve a raw path relative to workspace root and validate boundaries."""

		path = Path(raw_path)
		if not path.is_absolute():
			path = self.root / path

		resolved = path.resolve()

		if not self.is_within_root(resolved):
			raise SecurityError(f"Security violation: path escapes workspace: {raw_path}")

		return resolved