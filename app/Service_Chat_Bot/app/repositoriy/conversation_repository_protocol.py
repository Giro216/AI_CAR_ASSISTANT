from typing import Protocol


class ConversationRepository(Protocol):
	"""Protocol defining the interface for conversation repositories.
	
	This protocol allows for duck typing - any class implementing
	these methods can be used as a repository without explicit inheritance.
	"""

	def get_or_create_conversation_id(self, user_id: str, conversation_id: str | None) -> str:
		"""Gets an existing conversation id or creates a new one for the user."""
		...

	def add_message(self, conversation_id: str, role: str, content: str) -> None:
		"""Stores a new message in the repository."""
		...

	def load_messages(self, conversation_id: str) -> list[dict]:
		"""Returns full message history for the conversation."""
		...

	def load_prompt_messages(self, conversation_id: str) -> list[dict]:
		"""Loads messages for prompt context (hot context + summary)."""
		...

	def get_summary(self, conversation_id: str) -> str | None:
		"""Gets the current summary for a conversation."""
		...

	def set_summary(self, conversation_id: str, summary: str) -> None:
		"""Updates the summary for a conversation."""
		...

	def get_summary_cursor(self, conversation_id: str) -> int:
		"""Gets the cursor position for summary updates."""
		...

	def set_summary_cursor(self, conversation_id: str, cursor: int) -> None:
		"""Sets the cursor position for summary updates."""
		...

	def get_next_summary_batch(self, conversation_id: str) -> list | None:
		"""Gets the next batch of messages for summarization."""
		...

	def advance_summary(self, conversation_id: str, summary: str, batch_size: int) -> None:
		"""Advances the summary cursor and updates the summary."""
		...
