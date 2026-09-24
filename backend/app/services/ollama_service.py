import httpx

FORBIDDEN_CLAIMS = (
    "procederé",
    "procederemos",
    "actualizaré",
    "actualizaremos",
    "inmediatamente",
    "verificar su identidad",
    "verificar tu identidad",
    "no es posible",
    "no se puede modificar",
    "hemos realizado",
    "he realizado",
    "le informaremos",
    "te informaremos",
    "por favor, espere",
    "por favor espere",
    "sin realizar ninguna acción",
    "una vez finalizada",
)

SAFE_FALLBACK = (
    "Gracias por compartir tu solicitud. "
    "Revisaremos la información disponible y te indicaremos "
    "si necesitamos algún dato adicional. "
    "Cualquier cambio se confirmará únicamente después "
    "de evaluar el caso."
)


class OllamaServiceError(RuntimeError):
    pass


class OllamaService:
    def __init__(
        self,
        base_url: str = "http://127.0.0.1:11434",
        model: str = "qwen3.5:4b",
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model

    def generate_reply(
        self,
        subject: str,
        conversation: list[str],
    ) -> str:
        transcript = "\n".join(conversation)

        if not transcript:
            transcript = "No hay mensajes anteriores."

        prompt = (
            f"Asunto de la solicitud: {subject}\n\n"
            f"Conversación:\n{transcript}\n\n"
            "Redacta la siguiente respuesta que debería "
            "enviar el empleado."
        )

        try:
            response = httpx.post(
                f"{self._base_url}/api/chat",
                json={
                    "model": self._model,
                    "messages": [
                        {
                            "role": "system",
                            "content": (
                                "Eres un asistente que redacta borradores para "
                                "un empleado de soporte. Responde en español con "
                                "máximo 3 oraciones. Usa solamente hechos escritos "
                                "en el asunto y la conversación. "
                                "No inventes políticas, requisitos, verificaciones "
                                "de identidad, plazos, canales de contacto ni acciones. "
                                "Nunca prometas que una solicitud será realizada. "
                                "No uses expresiones como 'procederé', 'actualizaré', "
                                "'inmediatamente' o 'la modificación será realizada'. "
                                "Si faltan datos, pide solamente el dato directamente "
                                "necesario y explica que la solicitud será revisada. "
                                "Entrega una única respuesta, sin alternativas."
                            ),
                        },
                        {
                            "role": "user",
                            "content": prompt,
                        },
                    ],
                    "stream": False,
                    "think": False,
                    "options": {
                        "temperature": 0.0,
                        "num_predict": 100,
                    },
                },
                timeout=120.0,
            )

            response.raise_for_status()

            payload = response.json()
            content = payload["message"]["content"].strip()

        except (
            httpx.HTTPError,
            ValueError,
            KeyError,
            TypeError,
            AttributeError,
        ) as error:
            raise OllamaServiceError(
                "No se pudo generar la respuesta con Ollama."
            ) from error

        if not content:
            raise OllamaServiceError("Ollama devolvió una respuesta vacía.")

        normalized_content = content.casefold()

        has_unsupported_claim = any(
            claim.casefold() in normalized_content for claim in FORBIDDEN_CLAIMS
        )

        if has_unsupported_claim:
            return SAFE_FALLBACK

        return content
