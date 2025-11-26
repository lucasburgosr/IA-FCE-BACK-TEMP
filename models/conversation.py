from config.db_config import Base
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from models import conversation_prompt

class Conversation(Base):
    __tablename__ = "conversation"

    conversation_id = Column(String(255), primary_key=True)
    created_at = Column(DateTime(timezone=True), nullable=False)
    estudiante_id = Column(Integer, ForeignKey("estudiante.estudiante_id"), nullable=False)

    prompts = relationship(
        "Prompt", secondary=conversation_prompt, back_populates="conversations")
    sesiones = relationship(
        "SesionChat", back_populates="conversation", cascade="all, delete-orphan")