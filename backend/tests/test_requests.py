from fastapi.testclient import TestClient


def test_request_crud(
    client: TestClient,
) -> None:
    request_data = {
        "request_id": "TEST-001",
        "subject": "Necesito ayuda con mi pedido",
        "customer": "Cliente de prueba",
        "status": "Nueva",
        "priority": "Alta",
    }

    create_response = client.post(
        "/requests",
        json=request_data,
    )

    assert create_response.status_code == 201
    assert create_response.json() == {
        **request_data,
        "assignee": None,
    }

    list_response = client.get("/requests")

    assert list_response.status_code == 200
    assert len(list_response.json()) == 1
    assert list_response.json()[0]["request_id"] == "TEST-001"

    update_response = client.patch(
        "/requests/TEST-001",
        json={
            "status": "En proceso",
            "priority": "Media",
            "assignee": "Empleado conectado",
        },
    )

    assert update_response.status_code == 200

    updated_request = update_response.json()

    assert updated_request["status"] == "En proceso"
    assert updated_request["priority"] == "Media"
    assert updated_request["assignee"] == "Empleado conectado"

    unassign_response = client.patch(
        "/requests/TEST-001",
        json={"assignee": None},
    )

    assert unassign_response.status_code == 200
    assert unassign_response.json()["assignee"] is None

    delete_response = client.delete("/requests/TEST-001")

    assert delete_response.status_code == 204

    final_list_response = client.get("/requests")

    assert final_list_response.status_code == 200
    assert final_list_response.json() == []


def test_rejects_duplicate_request(
    client: TestClient,
) -> None:
    request_data = {
        "request_id": "TEST-002",
        "subject": "Solicitud duplicada",
        "customer": "Cliente de prueba",
        "status": "Nueva",
        "priority": "Alta",
    }

    first_response = client.post(
        "/requests",
        json=request_data,
    )
    duplicate_response = client.post(
        "/requests",
        json=request_data,
    )

    assert first_response.status_code == 201
    assert duplicate_response.status_code == 409
    assert duplicate_response.json()["detail"] == ("La solicitud TEST-002 ya existe.")


def test_update_missing_request(
    client: TestClient,
) -> None:
    response = client.patch(
        "/requests/NO-EXISTE",
        json={"status": "En proceso"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == ("La solicitud NO-EXISTE no existe.")


def test_rejects_empty_update(
    client: TestClient,
) -> None:
    client.post(
        "/requests",
        json={
            "request_id": "TEST-003",
            "subject": "Solicitud sin cambios",
            "customer": "Cliente de prueba",
            "status": "Nueva",
            "priority": "Baja",
        },
    )

    response = client.patch(
        "/requests/TEST-003",
        json={},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Debes enviar al menos un campo para actualizar."
    )


def test_validates_invalid_request_data(
    client: TestClient,
) -> None:
    response = client.post(
        "/requests",
        json={
            "request_id": "",
            "subject": "X",
            "customer": "A",
            "status": "Desconocida",
            "priority": "Urgente",
        },
    )

    assert response.status_code == 422
