from pydantic import BaseModel


class StatisticsSummaryResponse(BaseModel):
    total_requests: int
    status_counts: dict[str, int]
    priority_counts: dict[str, int]
