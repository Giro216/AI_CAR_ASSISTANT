from app.repositoriy.sql_conversation_repository import SqlConversationRepository


# def test_sql_repository_smoke(monkeypatch) -> None:
# 	# Skips when DATABASE_URL is not available in test env.
# 	import os
#
# 	if not os.getenv("DATABASE_URL"):
# 		return
#
# 	repository = SqlConversationRepository()
# 	conversation_id = repository.get_or_create_conversation_id("user-1", None)
# 	repository.add_message(conversation_id, "user", "hello")
# 	repository.add_message(conversation_id, "assistant", "hi")
#
# 	messages = repository.load_messages(conversation_id)
# 	assert len(messages) >= 2

