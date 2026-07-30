"""photo_upload_support

Make photo_registrations.device_id nullable (device_id NULL = master photo
not tied to a device) and add img_content_type for serving stored images.

Revision ID: 7f3a91c2d4b8
Revises: 263de27c0a92
Create Date: 2026-07-27

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7f3a91c2d4b8'
down_revision: Union[str, None] = '263de27c0a92'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('photo_registrations', 'device_id', existing_type=sa.Integer(), nullable=True)
    op.add_column('photo_registrations', sa.Column('img_content_type', sa.String(length=50), nullable=True))


def downgrade() -> None:
    op.drop_column('photo_registrations', 'img_content_type')
    # Rows with NULL device_id must be removed before restoring NOT NULL
    op.execute("DELETE FROM photo_registrations WHERE device_id IS NULL")
    op.alter_column('photo_registrations', 'device_id', existing_type=sa.Integer(), nullable=False)
