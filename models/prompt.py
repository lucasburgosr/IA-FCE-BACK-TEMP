from config.db_config import Base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from conversation_prompt import conversation_prompt


class Prompt(Base):
    __tablename__ = "prompt"

    prompt_id = Column(String(100), primary_key=True, index=True)
    materia_id = Column(Integer, ForeignKey(
        "materia.materia_id"), nullable=False)
    vs_temas_id = Column(String(50), nullable=False)
    vs_evaluaciones_id = Column(String(50), nullable=False)
    evaluador_id = Column(String(50), nullable=True)

    materia = relationship("Materia", back_populates="prompt")
    threads = relationship(
        "Conversation", secondary=conversation_prompt, back_populates="prompts")
    preguntas = relationship("Pregunta", back_populates="prompt")

    def __repr__(self):
        return f"<Prompt(prompt_id={self.prompt_id}>"
