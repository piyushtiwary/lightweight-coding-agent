"""Session serialization, disk persistence, and recovery manager."""

from datetime import datetime
import json
from pathlib import Path
from typing import Any, Dict, Optional
import uuid

from mini_coding_agent.context_utils import now_utc


def generate_session_id() -> str:
	"""Generate a chronological, unique session identifier."""

	return datetime.now().strftime("%Y%m%d-%H%M%S") + " - " + uuid.uuid4().hex[:6]


class SessionStore:
	"""Manage disk serialization and deserialization of agent sessions"""

	def __init__(self, root: Path | str):
		self.root = Path(root).resolve()
		self.root.mkdir(parents=True, exist_ok=True)


	def session_path(self, session_id: str) -> Path:
		"""Derive the absolute JSON file path for a session ID."""

		return self.root / f"{session_id}.json"


	def create_session(self, workspace_root: str) -> Dict[str, Any]:
		"""Initialize a fresh session dictionary"""

		session_id = generate_session_id()
		session: Dict[str, Any] = {
			"id": session_id,
			"created_at": now_utc(),
			"workspace_root": workspace_root,
			"history": [],
			"memory": {"task": "", "files": [], "notes": []},
		}
		self.save(session)
		return session


	def save(self, session: Dict[str, Any]) -> Path:
		"""Persist session dictionary to disk as formatted JSON."""

		path = self.session_path(session_id=session["id"])
		path.write_text(json.dumps(session, indent=2, ensure_ascii=False), encoding="utf-8")

		return path


	def load(self, session_id: str) -> Dict[str, Any]:
		"""Load an existing session from disk by ID"""

		path = self.session_path(session_id)
		if not path.is_file():
			raise FileNotFoundError(f"Session file not found: {path}")

		return json.load(path.read_text(encoding="utf-8"))


	def latest_session(self) -> Optional[str]:
		"""Identify the most recently modified session ID in the store."""

		json_file = sorted(self.root.glob("*.json"), key=lambda p: p.stat().st_mtime)
		return json_file[-1].stem if json_file else None
