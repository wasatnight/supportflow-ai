from dataclasses import dataclass


@dataclass(
    frozen=True,
    slots=True,
)
class SupportMessage:
    id: int
    sender: str
    content: str
    created_at: str
