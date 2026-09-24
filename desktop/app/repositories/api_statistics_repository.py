from typing import cast

import httpx

from app.models.statistics_summary import (
    StatisticsSummary,
)
from app.repositories.errors import (
    StatisticsRepositoryError,
)


class ApiStatisticsRepository:
    def __init__(
        self,
        base_url: str = "http://127.0.0.1:8000",
    ) -> None:
        self._base_url = base_url.rstrip("/")

    def get_summary(self) -> StatisticsSummary:
        try:
            response = httpx.get(
                f"{self._base_url}/statistics/summary",
                timeout=5.0,
            )

            response.raise_for_status()

            payload = cast(
                dict[str, object],
                response.json(),
            )

            status_counts = cast(
                dict[str, int],
                payload["status_counts"],
            )

            priority_counts = cast(
                dict[str, int],
                payload["priority_counts"],
            )

            return StatisticsSummary(
                total_requests=int(payload["total_requests"]),
                status_counts={
                    str(name): int(total) for name, total in status_counts.items()
                },
                priority_counts={
                    str(name): int(total) for name, total in priority_counts.items()
                },
            )

        except (
            httpx.HTTPError,
            ValueError,
            KeyError,
            TypeError,
        ) as error:
            raise StatisticsRepositoryError(
                "No se pudieron obtener las estadísticas."
            ) from error
