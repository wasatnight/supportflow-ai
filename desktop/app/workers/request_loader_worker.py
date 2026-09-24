from PySide6.QtCore import QObject, Signal, Slot

from app.repositories.api_request_repository import (
    ApiRequestRepository,
)
from app.repositories.errors import RequestRepositoryError


class RequestLoaderWorker(QObject):
    succeeded = Signal(list)
    failed = Signal(str)
    finished = Signal()

    def __init__(
        self,
        repository: ApiRequestRepository,
    ) -> None:
        super().__init__()

        self._repository = repository

    @Slot()
    def run(self) -> None:
        try:
            requests = self._repository.list_all()
        except RequestRepositoryError as error:
            self.failed.emit(str(error))
        else:
            self.succeeded.emit(requests)
        finally:
            self.finished.emit()
