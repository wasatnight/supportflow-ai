from fastapi.testclient import TestClient
from pytest import MonkeyPatch


def test_generate_ai_suggestion(
    client: TestClient,
    monkeypatch: MonkeyPatch,
) -> None:
    client.post(
        "/requests",
        json={
            "request_id": "AI-001",
            "subject": "Cambio de dirección",
            "customer": "Cliente de prueba",
            "status": "Nueva",
            "priority": "Media",
        },
    )

    client.post(
        "/requests/AI-001/messages",
        json={
            "sender": "Cliente",
            "content": "Necesito cambiar la dirección.",
        },
    )

    def fake_generate_reply(
        self: object,
        subject: str,
        conversation: list[str],
    ) -> str:
        assert subject == "Cambio de dirección"
        assert conversation == ["Cliente: Necesito cambiar la dirección."]

        return "Revisaremos su solicitud de cambio."

    monkeypatch.setattr(
        "app.main.OllamaService.generate_reply",
        fake_generate_reply,
    )

    response = client.post("/requests/AI-001/ai-suggestion")

    assert response.status_code == 200
    assert response.json() == {"suggestion": "Revisaremos su solicitud de cambio."}


def test_ai_requires_new_customer_message(
    client: TestClient,
) -> None:
    client.post(
        "/requests",
        json={
            "request_id": "AI-002",
            "subject": "Estado del pedido",
            "customer": "Cliente de prueba",
            "status": "En proceso",
            "priority": "Alta",
        },
    )

    client.post(
        "/requests/AI-002/messages",
        json={
            "sender": "Empleado",
            "content": "Estamos revisando su solicitud.",
        },
    )

    response = client.post("/requests/AI-002/ai-suggestion")

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "No hay un mensaje nuevo del cliente para responder."
    )


def test_ai_suggestion_for_missing_request(
    client: TestClient,
) -> None:
    response = client.post("/requests/NO-EXISTE/ai-suggestion")

    assert response.status_code == 404
    assert response.json()["detail"] == ("La solicitud NO-EXISTE no existe.")
