from sqlalchemy import select

from app.db.database import SessionLocal
from app.models.support_request import SupportRequest

INITIAL_REQUESTS = [
    {
        "request_id": "SOL-001",
        "subject": "Cobro duplicado en mi pedido",
        "customer": "Ana Torres",
        "status": "Nueva",
        "priority": "Alta",
    },
    {
        "request_id": "SOL-002",
        "subject": "Necesito cambiar la dirección de entrega",
        "customer": "Carlos Ruiz",
        "status": "En proceso",
        "priority": "Media",
    },
    {
        "request_id": "SOL-003",
        "subject": "No puedo descargar mi factura",
        "customer": "Laura Méndez",
        "status": "Resuelta",
        "priority": "Baja",
    },
    {
        "request_id": "SOL-004",
        "subject": "Mi pedido todavía no ha llegado",
        "customer": "Miguel Santos",
        "status": "Nueva",
        "priority": "Alta",
    },
]


def seed_database() -> None:
    with SessionLocal() as database:
        existing_ids = set(database.scalars(select(SupportRequest.request_id)).all())

        new_requests = [
            SupportRequest(**request_data)
            for request_data in INITIAL_REQUESTS
            if request_data["request_id"] not in existing_ids
        ]

        database.add_all(new_requests)
        database.commit()

        print(f"Solicitudes insertadas: {len(new_requests)}")


if __name__ == "__main__":
    seed_database()
