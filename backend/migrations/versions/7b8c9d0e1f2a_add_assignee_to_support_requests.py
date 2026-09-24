"""add assignee to support requests

Revision ID: 7b8c9d0e1f2a
Revises: 0a7abed5637b
Create Date: 2026-09-23

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "7b8c9d0e1f2a"
down_revision: Union[str, Sequence[str], None] = "0a7abed5637b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "support_requests",
        sa.Column(
            "assignee",
            sa.String(length=120),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("support_requests", "assignee")
