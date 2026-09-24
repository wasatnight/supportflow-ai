from PySide6.QtCore import QObject, Signal, Slot

from app.repositories.api_message_repository import (
    ApiMessageRepository,
)
from app.repositories.errors import RequestRepositoryError


class MessageCreateWorker(QObject):
    succeeded = Signal(object)
    failed = Signal(str)
    finished = Signal()

    def __init__(
        self,
        repository: ApiMessageRepository,
        request_id: str,
        content: str,
    ) -> None:
        super().__init__()
        self._repository = repository
        self._request_id = request_id
        self._content = content

    @Slot()
    def run(self) -> None:
        try:
            message = self._repository.create(
                request_id=self._request_id,
                sender="Empleado",
                content=self._content,
            )
        except RequestRepositoryError as error:
            self.failed.emit(str(error))
        else:
            self.succeeded.emit(message)
        finally:
            self.finished.emit()
