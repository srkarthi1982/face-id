"""add_type_columns_and_revert_device_fks

Revision ID: add_type_columns
Revises: 29531400f0e7
Create Date: 2026-07-20

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_type_columns'
down_revision = '29531400f0e7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add type column to locations table
    location_type_enum = sa.Enum('emirate', 'base', 'location', 'building', 'area', name='locationtype')
    location_type_enum.create(op.get_bind())
    
    op.add_column('locations', sa.Column('type', location_type_enum, nullable=False, server_default='location'))
    
    # Remove location_id and unit_id from devices table
    op.drop_constraint('devices_location_id_fkey', 'devices', type_='foreignkey')
    op.drop_constraint('devices_unit_id_fkey', 'devices', type_='foreignkey')
    op.drop_column('devices', 'location_id')
    op.drop_column('devices', 'unit_id')
    
    # Add location string column to devices table
    op.add_column('devices', sa.Column('location', sa.String(200), nullable=True))


def downgrade() -> None:
    # Remove location column from devices
    op.drop_column('devices', 'location')
    
    # Add back location_id and unit_id FKs
    op.add_column('devices', sa.Column('location_id', sa.Integer(), nullable=True))
    op.add_column('devices', sa.Column('unit_id', sa.Integer(), nullable=True))
    
    op.create_foreign_key(
        'devices_location_id_fkey',
        'devices', 'locations',
        ['location_id'], ['id']
    )
    op.create_foreign_key(
        'devices_unit_id_fkey',
        'devices', 'units',
        ['unit_id'], ['id']
    )
    
    # Remove type column from locations
    op.drop_column('locations', 'type')
    
    # Drop the enum type
    location_type_enum = sa.Enum('emirate', 'base', 'location', 'building', 'area', name='locationtype')
    location_type_enum.drop(op.get_bind())
