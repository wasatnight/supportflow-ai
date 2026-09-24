from fastapi.testclient import TestClient


def test_request_conversation(
    client: TestClient,
) -> None:
    create_request_response = client.post(
        "/requests",
        json={
            "request_id": "MSG-001",
            "subject": "Problema con mi pedido",
            "customer": "Cliente de prueba",
            "status": "Nueva",
            "priority": "Media",
        },
    )

    assert create_request_response.status_code == 201

    empty_conversation = client.get("/requests/MSG-001/messages")

    assert empty_conversation.status_code == 200
    assert empty_conversation.json() == []

    client_message = client.post(
        "/requests/MSG-001/messages",
        json={
            "sender": "Cliente",
            "content": "Necesito conocer el estado de mi pedido.",
        },
    )

    assert client_message.status_code == 201
    assert client_message.json()["sender"] == "Cliente"
    assert client_message.json()["content"] == (
        "Necesito conocer el estado de mi pedido."
    )

    employee_message = client.post(
        "/requests/MSG-001/messages",
        json={
            "sender": "Empleado",
            "content": "Estamos revisando su solicitud.",
        },
    )

    assert employee_message.status_code == 201
    assert employee_message.json()["sender"] == "Empleado"

    conversation_response = client.get("/requests/MSG-001/messages")

    assert conversation_response.status_code == 200

    conversation = conversation_response.json()

    assert len(conversation) == 2
    assert conversation[0]["sender"] == "Cliente"
    assert conversation[1]["sender"] == "Empleado"
    assert conversation[0]["created_at"]
    assert conversation[1]["created_at"]


def test_messages_for_missing_request(
    client: TestClient,
) -> None:
    response = client.get("/requests/NO-EXISTE/messages")

    assert response.status_code == 404
    assert response.json()["detail"] == ("La solicitud NO-EXISTE no existe.")
