"""add email and mac_address columns

Revision ID: 2279ba3b277e
Revises: 25318d8fad4e
Create Date: 2026-07-11 20:31:54.212104

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector

revision: str = '2279ba3b277e'
down_revision: Union[str, Sequence[str], None] = '25318d8fad4e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _column_exists(table: str, column: str) -> bool:
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    columns = [c["name"] for c in inspector.get_columns(table)]
    return column in columns


def upgrade() -> None:
    if not _column_exists("users", "email"):
        op.add_column("users", sa.Column("email", sa.String(length=100), nullable=True))
        op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    if not _column_exists("zones", "mac_address"):
        op.add_column("zones", sa.Column("mac_address", sa.String(length=50), nullable=True))


def downgrade() -> None:
    if _column_exists("users", "email"):
        op.drop_index(op.f("ix_users_email"), table_name="users")
        op.drop_column("users", "email")
    if _column_exists("zones", "mac_address"):
        op.drop_column("zones", "mac_address")
