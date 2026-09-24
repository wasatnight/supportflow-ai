from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

MessageSender = Literal[
    "Cliente",
    "Empleado",
    "IA",
]


class SupportMessageCreate(BaseModel):
    sender: MessageSender
    content: str = Field(
        min_length=1,
        max_length=5000,
    )


class SupportMessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sender: MessageSender
    content: str
    created_at: datetime
