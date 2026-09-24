from PySide6.QtCore import QObject, Signal, Slot

from app.repositories.api_statistics_repository import (
    ApiStatisticsRepository,
)
from app.repositories.errors import (
    StatisticsRepositoryError,
)


class StatisticsLoaderWorker(QObject):
    succeeded = Signal(object)
    failed = Signal(str)
    finished = Signal()

    def __init__(
        self,
        repository: ApiStatisticsRepository,
    ) -> None:
        super().__init__()
        self._repository = repository

    @Slot()
    def run(self) -> None:
        try:
            summary = self._repository.get_summary()
        except StatisticsRepositoryError as error:
            self.failed.emit(str(error))
        else:
            self.succeeded.emit(summary)
        finally:
            self.finished.emit()
