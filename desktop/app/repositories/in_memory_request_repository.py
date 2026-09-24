from app.models.support_request import SupportRequest


class InMemoryRequestRepository:
    def __init__(self) -> None:
        self._requests = [
            SupportRequest(
                "SOL-001",
                "Cobro duplicado en mi pedido",
                "Ana Torres",
                "Nueva",
                "Alta",
            ),
            SupportRequest(
                "SOL-002",
                "Necesito cambiar la dirección de entrega",
                "Carlos Ruiz",
                "En proceso",
                "Media",
            ),
            SupportRequest(
                "SOL-003",
                "No puedo descargar mi factura",
                "Laura Méndez",
                "Resuelta",
                "Baja",
            ),
            SupportRequest(
                "SOL-004",
                "Mi pedido todavía no ha llegado",
                "Miguel Santos",
                "Nueva",
                "Alta",
            ),
        ]

    def list_all(self) -> list[SupportRequest]:
        return list(self._requests)
