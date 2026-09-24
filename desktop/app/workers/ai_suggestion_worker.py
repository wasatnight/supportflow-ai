from PySide6.QtCore import QObject, Signal, Slot

from app.repositories.api_ai_repository import (
    ApiAiRepository,
)
from app.repositories.errors import AiRepositoryError


class AiSuggestionWorker(QObject):
    succeeded = Signal(str)
    failed = Signal(str)
    finished = Signal()

    def __init__(
        self,
        repository: ApiAiRepository,
        request_id: str,
    ) -> None:
        super().__init__()
        self._repository = repository
        self._request_id = request_id

    @Slot()
    def run(self) -> None:
        try:
            suggestion = self._repository.generate_suggestion(self._request_id)
        except AiRepositoryError as error:
            self.failed.emit(str(error))
        else:
            self.succeeded.emit(suggestion)
        finally:
            self.finished.emit()
