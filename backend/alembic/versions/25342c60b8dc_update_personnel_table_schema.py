"""update personnel table schema

Revision ID: 25342c60b8dc
Revises: 5a35db8d8ed5
Create Date: 2026-07-23

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '25342c60b8dc'
down_revision: Union[str, None] = '5a35db8d8ed5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new columns to personnel table
    op.add_column('personnel', sa.Column('org_id', sa.Integer(), nullable=True))
    op.add_column('personnel', sa.Column('emp_no', sa.String(length=64), nullable=False, server_default='TEMP'))
    op.add_column('personnel', sa.Column('full_name', sa.String(length=200), nullable=True))
    op.add_column('personnel', sa.Column('gender', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('personnel', sa.Column('email', sa.String(length=255), nullable=True))
    op.add_column('personnel', sa.Column('phone', sa.String(length=50), nullable=True))
    op.add_column('personnel', sa.Column('date_of_birth', sa.String(length=20), nullable=True))
    op.add_column('personnel', sa.Column('nationality', sa.String(length=100), nullable=True))
    op.add_column('personnel', sa.Column('department_id', sa.Integer(), nullable=True))
    op.add_column('personnel', sa.Column('position', sa.String(length=200), nullable=True))
    op.add_column('personnel', sa.Column('hire_date', sa.String(length=20), nullable=True))
    
    # Copy name to full_name and make it NOT NULL
    op.execute("UPDATE personnel SET full_name = name WHERE full_name IS NULL")
    op.execute("UPDATE personnel SET emp_no = person_id_internal WHERE emp_no = 'TEMP'")
    
    # Drop old name column
    op.drop_column('personnel', 'name')
    
    # Make full_name NOT NULL (remove server_default)
    op.alter_column('personnel', 'full_name', existing_type=sa.String(length=200), nullable=False)
    
    # Remove temp default from emp_no
    op.alter_column('personnel', 'emp_no', existing_type=sa.String(length=64), nullable=False, server_default=None)
    
    # Create foreign keys
    op.create_foreign_key(
        'fk_personnel_org_id_locations',
        'personnel', 'locations',
        ['org_id'], ['id'],
        ondelete='SET NULL'
    )
    op.create_foreign_key(
        'fk_personnel_department_id_locations',
        'personnel', 'locations',
        ['department_id'], ['id'],
        ondelete='SET NULL'
    )
    
    # Create indexes
    op.create_index('ix_personnel_org_id', 'personnel', ['org_id'], unique=False)
    op.create_index('ix_personnel_emp_no', 'personnel', ['emp_no'], unique=False)
    op.create_index('ix_personnel_department_id', 'personnel', ['department_id'], unique=False)
    op.create_index('ix_personnel_is_active', 'personnel', ['is_active'], unique=False)
    
    # Create unique constraint
    op.create_unique_constraint('uq_personnel_emp_no_org', 'personnel', ['emp_no', 'org_id'])


def downgrade() -> None:
    # Drop constraints and indexes
    op.drop_constraint('uq_personnel_emp_no_org', 'personnel', type_='unique')
    op.drop_index('ix_personnel_is_active', table_name='personnel')
    op.drop_index('ix_personnel_department_id', table_name='personnel')
    op.drop_index('ix_personnel_emp_no', table_name='personnel')
    op.drop_index('ix_personnel_org_id', table_name='personnel')
    
    # Drop foreign keys
    op.drop_constraint('fk_personnel_department_id_locations', 'personnel', type_='foreignkey')
    op.drop_constraint('fk_personnel_org_id_locations', 'personnel', type_='foreignkey')
    
    # Add back name column
    op.add_column('personnel', sa.Column('name', sa.String(length=200), nullable=True))
    op.execute("UPDATE personnel SET name = full_name")
    op.alter_column('personnel', 'name', nullable=False)
    
    # Drop new columns
    op.drop_column('personnel', 'hire_date')
    op.drop_column('personnel', 'position')
    op.drop_column('personnel', 'department_id')
    op.drop_column('personnel', 'nationality')
    op.drop_column('personnel', 'date_of_birth')
    op.drop_column('personnel', 'phone')
    op.drop_column('personnel', 'email')
    op.drop_column('personnel', 'gender')
    op.drop_column('personnel', 'full_name')
    op.drop_column('personnel', 'emp_no')
    op.drop_column('personnel', 'org_id')
