from PySide6.QtCore import QObject, Signal, Slot

from app.repositories.api_message_repository import (
    ApiMessageRepository,
)
from app.repositories.errors import RequestRepositoryError


class MessageLoaderWorker(QObject):
    succeeded = Signal(list)
    failed = Signal(str)
    finished = Signal()

    def __init__(
        self,
        repository: ApiMessageRepository,
        request_id: str,
    ) -> None:
        super().__init__()
        self._repository = repository
        self._request_id = request_id

    @Slot()
    def run(self) -> None:
        try:
            messages = self._repository.list_by_request(self._request_id)
        except RequestRepositoryError as error:
            self.failed.emit(str(error))
        else:
            self.succeeded.emit(messages)
        finally:
            self.finished.emit()
