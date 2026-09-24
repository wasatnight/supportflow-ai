from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

RequestStatus = Literal["Nueva", "En proceso", "Resuelta"]
RequestPriority = Literal["Alta", "Media", "Baja"]


class SupportRequestCreate(BaseModel):
    request_id: str = Field(min_length=1, max_length=20)
    subject: str = Field(min_length=3, max_length=200)
    customer: str = Field(min_length=2, max_length=120)
    status: RequestStatus = "Nueva"
    priority: RequestPriority
    assignee: str | None = Field(default=None, min_length=2, max_length=120)


class SupportRequestUpdate(BaseModel):
    status: RequestStatus | None = None
    priority: RequestPriority | None = None
    assignee: str | None = Field(default=None, min_length=2, max_length=120)


class SupportRequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    request_id: str
    subject: str
    customer: str
    status: RequestStatus
    priority: RequestPriority
    assignee: str | None
