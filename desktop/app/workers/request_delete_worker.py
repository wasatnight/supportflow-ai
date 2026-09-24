from PySide6.QtCore import QObject, Signal, Slot

from app.repositories.api_request_repository import (
    ApiRequestRepository,
)
from app.repositories.errors import RequestRepositoryError


class RequestDeleteWorker(QObject):
    succeeded = Signal(str)
    failed = Signal(str)
    finished = Signal()

    def __init__(
        self,
        repository: ApiRequestRepository,
        request_id: str,
    ) -> None:
        super().__init__()

        self._repository = repository
        self._request_id = request_id

    @Slot()
    def run(self) -> None:
        try:
            self._repository.delete(self._request_id)
        except RequestRepositoryError as error:
            self.failed.emit(str(error))
        else:
            self.succeeded.emit(self._request_id)
        finally:
            self.finished.emit()
