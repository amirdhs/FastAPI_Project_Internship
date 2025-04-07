from pydantic import BaseModel

class ConversationInput(BaseModel):
    message: str

class ConversationOutput(BaseModel):
    emotion: str
    response: str
