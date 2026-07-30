"""Normalize unit type enum values to match the application model.

Revision ID: 9b7d3e21a4f0
Revises: 7f3a91c2d4b8
Create Date: 2026-07-30
"""

from typing import Sequence, Union

from alembic import op


revision: str = "9b7d3e21a4f0"
down_revision: Union[str, None] = "7f3a91c2d4b8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE unittype RENAME VALUE 'FORCE' TO 'force'")
    op.execute("ALTER TYPE unittype RENAME VALUE 'COMMAND' TO 'command'")
    op.execute("ALTER TYPE unittype RENAME VALUE 'BATTALION' TO 'battalion'")
    op.execute("ALTER TYPE unittype RENAME VALUE 'UNIT' TO 'unit'")


def downgrade() -> None:
    op.execute("ALTER TYPE unittype RENAME VALUE 'force' TO 'FORCE'")
    op.execute("ALTER TYPE unittype RENAME VALUE 'command' TO 'COMMAND'")
    op.execute("ALTER TYPE unittype RENAME VALUE 'battalion' TO 'BATTALION'")
    op.execute("ALTER TYPE unittype RENAME VALUE 'unit' TO 'UNIT'")
