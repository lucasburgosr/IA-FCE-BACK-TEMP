from sqlalchemy import Table, Column, ForeignKey, String
from config.db_config import Base

conversation_prompt = Table(
    "conversation_prompt",
    Base.metadata,
    Column("conversation_id", String, ForeignKey("conversation.conversation_id"), primary_key=True),
    Column("prompt_id", String, ForeignKey(
        "prompt.prompt_id"), primary_key=True)
)
