from typing import cast

import httpx

from app.models.support_message import SupportMessage
from app.repositories.errors import RequestRepositoryError


class ApiMessageRepository:
    def __init__(
        self,
        base_url: str = "http://127.0.0.1:8000",
    ) -> None:
        self._base_url = base_url.rstrip("/")

    def list_by_request(
        self,
        request_id: str,
    ) -> list[SupportMessage]:
        try:
            response = httpx.get(
                (f"{self._base_url}/requests/" f"{request_id}/messages"),
                timeout=5.0,
            )

            response.raise_for_status()

            payload = cast(
                list[dict[str, str | int]],
                response.json(),
            )

            return [self._to_message(item) for item in payload]

        except (
            httpx.HTTPError,
            ValueError,
            KeyError,
            TypeError,
        ) as error:
            raise RequestRepositoryError(
                "No se pudo obtener la conversación."
            ) from error

    def create(
        self,
        request_id: str,
        sender: str,
        content: str,
    ) -> SupportMessage:
        try:
            response = httpx.post(
                (f"{self._base_url}/requests/" f"{request_id}/messages"),
                json={
                    "sender": sender,
                    "content": content,
                },
                timeout=5.0,
            )

            response.raise_for_status()

            payload = cast(
                dict[str, str | int],
                response.json(),
            )

            return self._to_message(payload)

        except (
            httpx.HTTPError,
            ValueError,
            KeyError,
            TypeError,
        ) as error:
            raise RequestRepositoryError("No se pudo guardar el mensaje.") from error

    @staticmethod
    def _to_message(
        payload: dict[str, str | int],
    ) -> SupportMessage:
        return SupportMessage(
            id=int(payload["id"]),
            sender=str(payload["sender"]),
            content=str(payload["content"]),
            created_at=str(payload["created_at"]),
        )
