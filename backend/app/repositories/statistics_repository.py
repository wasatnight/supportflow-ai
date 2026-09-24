from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.support_request import SupportRequest


class StatisticsRepository:
    def __init__(
        self,
        database: Session,
    ) -> None:
        self._database = database

    def get_summary(
        self,
    ) -> tuple[
        int,
        dict[str, int],
        dict[str, int],
    ]:
        total_statement = select(func.count(SupportRequest.id))

        total_requests = int(self._database.scalar(total_statement) or 0)

        status_counts = {
            "Nueva": 0,
            "En proceso": 0,
            "Resuelta": 0,
        }

        status_statement = select(
            SupportRequest.status,
            func.count(SupportRequest.id),
        ).group_by(SupportRequest.status)

        for request_status, total in self._database.execute(status_statement):
            status_counts[str(request_status)] = int(total)

        priority_counts = {
            "Alta": 0,
            "Media": 0,
            "Baja": 0,
        }

        priority_statement = select(
            SupportRequest.priority,
            func.count(SupportRequest.id),
        ).group_by(SupportRequest.priority)

        for priority, total in self._database.execute(priority_statement):
            priority_counts[str(priority)] = int(total)

        return (
            total_requests,
            status_counts,
            priority_counts,
        )
