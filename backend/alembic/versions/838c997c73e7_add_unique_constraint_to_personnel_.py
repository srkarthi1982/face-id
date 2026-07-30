"""add_unique_constraint_to_personnel_person_id_internal

Revision ID: 838c997c73e7
Revises: 25342c60b8dc
Create Date: 2026-07-23 10:33:57.140608

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '838c997c73e7'
down_revision: Union[str, None] = '25342c60b8dc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add unique constraint to personnel.person_id_internal
    # This is required for foreign key references from photo_registrations and device_person_mapping
    op.create_unique_constraint('uq_personnel_person_id_internal', 'personnel', ['person_id_internal'])


def downgrade() -> None:
    # Drop unique constraint
    op.drop_constraint('uq_personnel_person_id_internal', 'personnel', type_='unique')
