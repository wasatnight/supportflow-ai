from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class StatisticsSummary:
    total_requests: int
    status_counts: dict[str, int]
    priority_counts: dict[str, int]

    @property
    def resolution_percentage(self) -> float:
        if self.total_requests == 0:
            return 0.0

        resolved = self.status_counts.get(
            "Resuelta",
            0,
        )

        return (resolved / self.total_requests) * 100
