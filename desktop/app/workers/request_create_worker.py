from PySide6.QtCore import QObject, Signal, Slot

from app.models.support_request import SupportRequest
from app.repositories.api_request_repository import (
    ApiRequestRepository,
)
from app.repositories.errors import RequestRepositoryError


class RequestCreateWorker(QObject):
    succeeded = Signal(object)
    failed = Signal(str)
    finished = Signal()

    def __init__(
        self,
        repository: ApiRequestRepository,
        request: SupportRequest,
    ) -> None:
        super().__init__()

        self._repository = repository
        self._request = request

    @Slot()
    def run(self) -> None:
        try:
            created_request = self._repository.create(self._request)
        except RequestRepositoryError as error:
            self.failed.emit(str(error))
        else:
            self.succeeded.emit(created_request)
        finally:
            self.finished.emit()
