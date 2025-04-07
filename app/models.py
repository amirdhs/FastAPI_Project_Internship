from sqlalchemy import Column, Integer, String, DateTime, func
from .database import Base

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_message = Column(String, nullable=False)
    emotion = Column(String, nullable=False)
    bot_response = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
