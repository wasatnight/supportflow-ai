from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.support_request import SupportRequest
from app.schemas.support_request import (
    SupportRequestCreate,
    SupportRequestUpdate,
)


class SupportRequestRepository:
    def __init__(self, database: Session) -> None:
        self._database = database

    def list_all(self) -> list[SupportRequest]:
        statement = select(SupportRequest).order_by(SupportRequest.id)

        return list(self._database.scalars(statement))

    def get_by_request_id(
        self,
        request_id: str,
    ) -> SupportRequest | None:
        statement = select(SupportRequest).where(
            SupportRequest.request_id == request_id
        )

        return self._database.scalar(statement)

    def update(
        self,
        request: SupportRequest,
        update_data: SupportRequestUpdate,
    ) -> SupportRequest:
        changes = update_data.model_dump(exclude_unset=True)

        for field, value in changes.items():
            setattr(request, field, value)

        try:
            self._database.commit()
        except SQLAlchemyError:
            self._database.rollback()
            raise

        self._database.refresh(request)

        return request

    def create(
        self,
        request_data: SupportRequestCreate,
    ) -> SupportRequest:
        request = SupportRequest(**request_data.model_dump())

        self._database.add(request)

        try:
            self._database.commit()
        except SQLAlchemyError:
            self._database.rollback()
            raise

        self._database.refresh(request)

        return request

    def delete(
        self,
        request: SupportRequest,
    ) -> None:
        self._database.delete(request)

        try:
            self._database.commit()
        except SQLAlchemyError:
            self._database.rollback()
            raise
