"""rename_authority_unit_to_unit

Revision ID: 50f6ed33ec34
Revises: add_type_columns
Create Date: 2026-07-21 08:10:26.995777

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '50f6ed33ec34'
down_revision: Union[str, None] = 'add_type_columns'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Rename column in locations table
    op.alter_column('locations', 'authority_unit_id', new_column_name='unit_id')


def downgrade() -> None:
    # Revert column name in locations table
    op.alter_column('locations', 'unit_id', new_column_name='authority_unit_id')
