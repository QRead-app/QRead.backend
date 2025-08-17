"""Add app_settings

Revision ID: 31e6ea4e0dfa
Revises: 721ef0b6f689
Create Date: 2025-08-17 21:56:43.699041

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '31e6ea4e0dfa'
down_revision: Union[str, Sequence[str], None] = '721ef0b6f689'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "app_settings",
        sa.Column('key', sa.String(), nullable=False, primary_key=True),
        sa.Column('value', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('key')   
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("app_settings")
