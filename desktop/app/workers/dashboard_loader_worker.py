from PySide6.QtCore import QObject, Signal, Slot

from app.models.dashboard_data import DashboardData
from app.repositories.api_request_repository import ApiRequestRepository
from app.repositories.api_statistics_repository import ApiStatisticsRepository
from app.repositories.errors import (
    RequestRepositoryError,
    StatisticsRepositoryError,
)


class DashboardLoaderWorker(QObject):
    succeeded = Signal(object)
    failed = Signal(str)
    finished = Signal()

    def __init__(
        self,
        statistics_repository: ApiStatisticsRepository,
        request_repository: ApiRequestRepository,
    ) -> None:
        super().__init__()
        self._statistics_repository = statistics_repository
        self._request_repository = request_repository

    @Slot()
    def run(self) -> None:
        try:
            statistics = self._statistics_repository.get_summary()
            requests = self._request_repository.list_all()

            data = DashboardData(
                statistics=statistics,
                recent_requests=list(reversed(requests[-5:])),
            )
        except (
            RequestRepositoryError,
            StatisticsRepositoryError,
        ) as error:
            self.failed.emit(str(error))
        else:
            self.succeeded.emit(data)
        finally:
            self.finished.emit()
