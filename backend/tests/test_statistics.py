from fastapi.testclient import TestClient


def test_statistics_summary(
    client: TestClient,
) -> None:
    requests = [
        {
            "request_id": "STAT-001",
            "subject": "Primera solicitud",
            "customer": "Cliente uno",
            "status": "Nueva",
            "priority": "Alta",
        },
        {
            "request_id": "STAT-002",
            "subject": "Segunda solicitud",
            "customer": "Cliente dos",
            "status": "Nueva",
            "priority": "Alta",
        },
        {
            "request_id": "STAT-003",
            "subject": "Tercera solicitud",
            "customer": "Cliente tres",
            "status": "En proceso",
            "priority": "Media",
        },
        {
            "request_id": "STAT-004",
            "subject": "Cuarta solicitud",
            "customer": "Cliente cuatro",
            "status": "Resuelta",
            "priority": "Baja",
        },
    ]

    for request_data in requests:
        response = client.post(
            "/requests",
            json=request_data,
        )

        assert response.status_code == 201

    response = client.get("/statistics/summary")

    assert response.status_code == 200
    assert response.json() == {
        "total_requests": 4,
        "status_counts": {
            "Nueva": 2,
            "En proceso": 1,
            "Resuelta": 1,
        },
        "priority_counts": {
            "Alta": 2,
            "Media": 1,
            "Baja": 1,
        },
    }
