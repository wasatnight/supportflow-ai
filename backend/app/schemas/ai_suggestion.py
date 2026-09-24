from pydantic import BaseModel


class AiSuggestionResponse(BaseModel):
    suggestion: str
