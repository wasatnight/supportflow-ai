from dataclasses import asdict
from typing import cast

import httpx

from app.models.support_request import SupportRequest
from app.repositories.errors import RequestRepositoryError


class ApiRequestRepository:
    def __init__(
        self,
        base_url: str = "http://127.0.0.1:8000",
    ) -> None:
        self._base_url = base_url.rstrip("/")

    def list_all(self) -> list[SupportRequest]:
        try:
            response = httpx.get(
                f"{self._base_url}/requests",
                timeout=5.0,
            )

            response.raise_for_status()

            payload = cast(
                list[dict[str, str]],
                response.json(),
            )

            return [SupportRequest(**item) for item in payload]

        except (
            httpx.HTTPError,
            ValueError,
            TypeError,
        ) as error:
            raise RequestRepositoryError(
                "No se pudieron obtener las solicitudes del servidor."
            ) from error

    def create(self, request: SupportRequest) -> SupportRequest:
        try:
            response = httpx.post(
                f"{self._base_url}/requests",
                json=asdict(request),
                timeout=5.0,
            )

            response.raise_for_status()

            payload = cast(
                dict[str, str],
                response.json(),
            )

            return SupportRequest(**payload)

        except httpx.HTTPStatusError as error:
            if error.response.status_code == 409:
                raise RequestRepositoryError(
                    f"La solicitud {request.request_id} ya existe."
                ) from error

            raise RequestRepositoryError("No se pudo crear la solicitud.") from error

        except (
            httpx.HTTPError,
            ValueError,
            TypeError,
        ) as error:
            raise RequestRepositoryError(
                "No se pudo conectar con el servidor."
            ) from error

    def update(
        self,
        request_id: str,
        status: str,
        priority: str,
        assignee: str | None,
    ) -> SupportRequest:
        try:
            response = httpx.patch(
                f"{self._base_url}/requests/{request_id}",
                json={
                    "status": status,
                    "priority": priority,
                    "assignee": assignee,
                },
                timeout=5.0,
            )

            response.raise_for_status()

            payload = cast(
                dict[str, str],
                response.json(),
            )

            return SupportRequest(**payload)

        except httpx.HTTPStatusError as error:
            if error.response.status_code == 404:
                raise RequestRepositoryError(
                    f"La solicitud {request_id} no existe."
                ) from error

            raise RequestRepositoryError(
                "No se pudo actualizar la solicitud."
            ) from error

        except (
            httpx.HTTPError,
            ValueError,
            TypeError,
        ) as error:
            raise RequestRepositoryError(
                "No se pudo conectar con el servidor."
            ) from error

    def delete(
        self,
        request_id: str,
    ) -> None:
        try:
            response = httpx.delete(
                f"{self._base_url}/requests/{request_id}",
                timeout=5.0,
            )

            response.raise_for_status()

        except httpx.HTTPStatusError as error:
            if error.response.status_code == 404:
                raise RequestRepositoryError(
                    f"La solicitud {request_id} no existe."
                ) from error

            raise RequestRepositoryError("No se pudo eliminar la solicitud.") from error

        except httpx.HTTPError as error:
            raise RequestRepositoryError(
                "No se pudo conectar con el servidor."
            ) from error
