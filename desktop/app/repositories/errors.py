class RequestRepositoryError(RuntimeError):
    """Error al consultar la fuente de solicitudes."""


class AiRepositoryError(RuntimeError):
    """Error al solicitar una sugerencia de IA."""


class StatisticsRepositoryError(RuntimeError):
    """Error al consultar las estadísticas."""
