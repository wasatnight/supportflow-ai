from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from typing import Annotated

from fastapi import (
    Depends,
    FastAPI,
    HTTPException,
    Response,
    status,
)

from app.core.config import settings
from app.db.database import initialize_database

from sqlalchemy.exc import IntegrityError

from app.db.dependencies import get_db
from app.models.support_request import SupportRequest
from app.repositories import (
    StatisticsRepository,
    SupportMessageRepository,
    SupportRequestRepository,
)
from app.schemas.statistics import (
    StatisticsSummaryResponse,
)
from app.schemas.support_request import (
    SupportRequestCreate,
    SupportRequestResponse,
    SupportRequestUpdate,
)
from app.schemas.support_message import (
    SupportMessageCreate,
    SupportMessageResponse,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.models.support_message import SupportMessage
from app.schemas.ai_suggestion import AiSuggestionResponse
from app.services import OllamaService, OllamaServiceError


@asynccontextmanager
async def lifespan(
    _: FastAPI,
) -> AsyncIterator[None]:
    if settings.database_mode == "sqlite":
        initialize_database()

    yield


app = FastAPI(
    title="SupportFlow AI API",
    description="API para la gestión inteligente de solicitudes.",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health", tags=["Sistema"])
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "supportflow-api",
    }


@app.get(
    "/requests",
    response_model=list[SupportRequestResponse],
    tags=["Solicitudes"],
)
def list_requests(
    database: Annotated[Session, Depends(get_db)],
) -> list[SupportRequest]:
    repository = SupportRequestRepository(database)

    return repository.list_all()


@app.post(
    "/requests",
    response_model=SupportRequestResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Solicitudes"],
)
def create_request(
    request_data: SupportRequestCreate,
    database: Annotated[Session, Depends(get_db)],
) -> SupportRequest:
    repository = SupportRequestRepository(database)

    try:
        return repository.create(request_data)
    except IntegrityError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"La solicitud {request_data.request_id} ya existe.",
        ) from error


@app.patch(
    "/requests/{request_id}",
    response_model=SupportRequestResponse,
    tags=["Solicitudes"],
)
def update_request(
    request_id: str,
    update_data: SupportRequestUpdate,
    database: Annotated[Session, Depends(get_db)],
) -> SupportRequest:
    repository = SupportRequestRepository(database)

    request = repository.get_by_request_id(request_id)

    if request is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"La solicitud {request_id} no existe.",
        )

    if not update_data.model_fields_set:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debes enviar al menos un campo para actualizar.",
        )

    return repository.update(
        request,
        update_data,
    )


@app.delete(
    "/requests/{request_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Solicitudes"],
)
def delete_request(
    request_id: str,
    database: Annotated[Session, Depends(get_db)],
) -> Response:
    repository = SupportRequestRepository(database)

    request = repository.get_by_request_id(request_id)

    if request is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"La solicitud {request_id} no existe.",
        )

    repository.delete(request)

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get(
    "/requests/{request_id}/messages",
    response_model=list[SupportMessageResponse],
    tags=["Conversación"],
)
def list_messages(
    request_id: str,
    database: Annotated[Session, Depends(get_db)],
) -> list[SupportMessage]:
    request_repository = SupportRequestRepository(database)
    message_repository = SupportMessageRepository(database)

    request = request_repository.get_by_request_id(request_id)

    if request is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"La solicitud {request_id} no existe.",
        )

    return message_repository.list_by_request(request.id)


@app.post(
    "/requests/{request_id}/messages",
    response_model=SupportMessageResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Conversación"],
)
def create_message(
    request_id: str,
    message_data: SupportMessageCreate,
    database: Annotated[Session, Depends(get_db)],
) -> SupportMessage:
    request_repository = SupportRequestRepository(database)
    message_repository = SupportMessageRepository(database)

    request = request_repository.get_by_request_id(request_id)

    if request is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"La solicitud {request_id} no existe.",
        )

    return message_repository.create(
        support_request_id=request.id,
        message_data=message_data,
    )


@app.post(
    "/requests/{request_id}/ai-suggestion",
    response_model=AiSuggestionResponse,
    tags=["IA"],
)
def generate_ai_suggestion(
    request_id: str,
    database: Annotated[Session, Depends(get_db)],
) -> AiSuggestionResponse:
    request_repository = SupportRequestRepository(database)
    message_repository = SupportMessageRepository(database)

    support_request = request_repository.get_by_request_id(request_id)

    if support_request is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"La solicitud {request_id} no existe.",
        )

    messages = message_repository.list_by_request(support_request.id)
    if messages and messages[-1].sender != "Cliente":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=("No hay un mensaje nuevo del cliente " "para responder."),
        )

    conversation = [f"{message.sender}: {message.content}" for message in messages]

    service = OllamaService()

    try:
        suggestion = service.generate_reply(
            subject=support_request.subject,
            conversation=conversation,
        )
    except OllamaServiceError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(error),
        ) from error

    return AiSuggestionResponse(suggestion=suggestion)


@app.get(
    "/statistics/summary",
    response_model=StatisticsSummaryResponse,
    tags=["Estadísticas"],
)
def get_statistics_summary(
    database: Annotated[Session, Depends(get_db)],
) -> StatisticsSummaryResponse:
    repository = StatisticsRepository(database)

    (
        total_requests,
        status_counts,
        priority_counts,
    ) = repository.get_summary()

    return StatisticsSummaryResponse(
        total_requests=total_requests,
        status_counts=status_counts,
        priority_counts=priority_counts,
    )
