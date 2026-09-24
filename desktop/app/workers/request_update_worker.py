from PySide6.QtCore import QObject, Signal, Slot

from app.repositories.api_request_repository import (
    ApiRequestRepository,
)
from app.repositories.errors import RequestRepositoryError


class RequestUpdateWorker(QObject):
    succeeded = Signal(object)
    failed = Signal(str)
    finished = Signal()

    def __init__(
        self,
        repository: ApiRequestRepository,
        request_id: str,
        status: str,
        priority: str,
        assignee: str | None,
    ) -> None:
        super().__init__()

        self._repository = repository
        self._request_id = request_id
        self._status = status
        self._priority = priority
        self._assignee = assignee

    @Slot()
    def run(self) -> None:
        try:
            updated_request = self._repository.update(
                request_id=self._request_id,
                status=self._status,
                priority=self._priority,
                assignee=self._assignee,
            )
        except RequestRepositoryError as error:
            self.failed.emit(str(error))
        else:
            self.succeeded.emit(updated_request)
        finally:
            self.finished.emit()
