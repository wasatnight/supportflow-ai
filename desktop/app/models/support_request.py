from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SupportRequest:
    request_id: str
    subject: str
    customer: str
    status: str
    priority: str
    assignee: str | None = None
