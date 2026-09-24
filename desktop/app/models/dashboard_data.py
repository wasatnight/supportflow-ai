from dataclasses import dataclass

from app.models.statistics_summary import StatisticsSummary
from app.models.support_request import SupportRequest


@dataclass(frozen=True, slots=True)
class DashboardData:
    statistics: StatisticsSummary
    recent_requests: list[SupportRequest]
