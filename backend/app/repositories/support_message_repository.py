from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.support_message import SupportMessage
from app.schemas.support_message import (
    SupportMessageCreate,
)


class SupportMessageRepository:
    def __init__(
        self,
        database: Session,
    ) -> None:
        self._database = database

    def list_by_request(
        self,
        support_request_id: int,
    ) -> list[SupportMessage]:
        statement = (
            select(SupportMessage)
            .where(SupportMessage.support_request_id == support_request_id)
            .order_by(
                SupportMessage.created_at,
                SupportMessage.id,
            )
        )

        return list(self._database.scalars(statement))

    def create(
        self,
        support_request_id: int,
        message_data: SupportMessageCreate,
    ) -> SupportMessage:
        message = SupportMessage(
            support_request_id=support_request_id,
            **message_data.model_dump(),
        )

        self._database.add(message)

        try:
            self._database.commit()
        except SQLAlchemyError:
            self._database.rollback()
            raise

        self._database.refresh(message)

        return message
