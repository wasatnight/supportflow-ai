from typing import cast

import httpx

from app.repositories.errors import AiRepositoryError


class ApiAiRepository:
    def __init__(
        self,
        base_url: str = "http://127.0.0.1:8000",
    ) -> None:
        self._base_url = base_url.rstrip("/")

    def generate_suggestion(
        self,
        request_id: str,
    ) -> str:
        try:
            response = httpx.post(
                (f"{self._base_url}/requests/" f"{request_id}/ai-suggestion"),
                timeout=120.0,
            )

            response.raise_for_status()

            payload = cast(
                dict[str, str],
                response.json(),
            )

            suggestion = payload["suggestion"].strip()

            if not suggestion:
                raise ValueError("La sugerencia está vacía.")

            return suggestion

        except httpx.HTTPStatusError as error:
            try:
                error_payload = error.response.json()
                detail = str(
                    error_payload.get(
                        "detail",
                        "No se pudo generar la sugerencia.",
                    )
                )
            except (
                ValueError,
                AttributeError,
            ):
                detail = "No se pudo generar la sugerencia de IA."

            raise AiRepositoryError(detail) from error

        except (
            httpx.RequestError,
            ValueError,
            KeyError,
            TypeError,
        ) as error:
            raise AiRepositoryError(
                "No se pudo generar la sugerencia de IA."
            ) from error
