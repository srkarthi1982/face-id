"""departments timings postgres dashboard

Revision ID: 4f6a2c9d8b13
Revises: 9b7d3e21a4f0
Create Date: 2026-08-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "4f6a2c9d8b13"
down_revision: Union[str, None] = "9b7d3e21a4f0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


WEEKDAY_ENUM = postgresql.ENUM(
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
    name="weekday",
    create_type=False,
)


def upgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'weekday') THEN
                CREATE TYPE weekday AS ENUM (
                    'monday', 'tuesday', 'wednesday', 'thursday',
                    'friday', 'saturday', 'sunday'
                );
            END IF;
        END$$;
        """
    )

    op.create_table(
        "departments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("code", sa.String(length=100), nullable=True),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("parent_id", sa.Integer(), nullable=True),
        sa.Column("path", sa.String(length=1000), nullable=False, server_default="/"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["parent_id"], ["departments.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_departments_parent_id", "departments", ["parent_id"], unique=False)
    op.create_index("ix_departments_is_active", "departments", ["is_active"], unique=False)

    # Preserve existing location-backed personnel department references by
    # creating Department rows with matching IDs before the FK is converted.
    op.execute(
        """
        INSERT INTO departments (id, name, code, description, parent_id, path, is_active, sort_order, created_at, updated_at)
        SELECT DISTINCT l.id, l.name, NULL::varchar, 'Migrated from locations for personnel department mapping',
               NULL::integer, COALESCE(l.path, '/' || l.name), COALESCE(l.is_active, true),
               COALESCE(l.sort_order, 0), COALESCE(l.created_at, now()), COALESCE(l.updated_at, now())
        FROM personnel p
        JOIN locations l ON l.id = p.department_id
        WHERE p.department_id IS NOT NULL
        ON CONFLICT (id) DO NOTHING
        """
    )
    op.execute("SELECT setval(pg_get_serial_sequence('departments', 'id'), GREATEST((SELECT COALESCE(MAX(id), 0) FROM departments) + 1, 1), false)")

    op.drop_constraint("fk_personnel_department_id_locations", "personnel", type_="foreignkey")
    op.execute(
        """
        UPDATE personnel
        SET department_id = NULL
        WHERE department_id IS NOT NULL
          AND department_id NOT IN (SELECT id FROM departments)
        """
    )
    op.create_foreign_key(
        "fk_personnel_department_id_departments",
        "personnel",
        "departments",
        ["department_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.create_table(
        "timings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("department_id", sa.Integer(), nullable=False),
        sa.Column("start_day", WEEKDAY_ENUM, nullable=False),
        sa.Column("end_day", WEEKDAY_ENUM, nullable=False),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("end_time", sa.Time(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("start_time < end_time", name="ck_timings_start_before_end"),
        sa.ForeignKeyConstraint(["department_id"], ["departments.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_timings_department_id", "timings", ["department_id"], unique=False)
    op.create_index(
        "uq_timings_one_active_per_department",
        "timings",
        ["department_id"],
        unique=True,
        postgresql_where=sa.text("is_active IS TRUE"),
    )

    for index_name, column in (
        ("ix_recognition_records_device_id", "device_id"),
        ("ix_recognition_records_person_id_internal", "person_id_internal"),
        ("ix_recognition_records_event_time", "event_time"),
        ("ix_recognition_records_created_at", "created_at"),
    ):
        op.create_index(index_name, "recognition_records", [column], unique=False, if_not_exists=True)

    op.execute(
        """
        INSERT INTO permissions (code, name, description, module)
        VALUES
          ('department:read', 'Read Departments', 'View department hierarchy', 'master-data'),
          ('department:write', 'Write Departments', 'Create, update, delete departments', 'master-data'),
          ('timing:read', 'Read Timings', 'View department timing rules', 'master-data'),
          ('timing:write', 'Write Timings', 'Create, update, delete department timing rules', 'master-data')
        ON CONFLICT (code) DO NOTHING
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DELETE FROM permissions
        WHERE code IN ('department:read', 'department:write', 'timing:read', 'timing:write')
        """
    )
    op.drop_index("uq_timings_one_active_per_department", table_name="timings")
    op.drop_index("ix_timings_department_id", table_name="timings")
    op.drop_table("timings")

    for index_name in (
        "ix_recognition_records_created_at",
        "ix_recognition_records_event_time",
        "ix_recognition_records_person_id_internal",
        "ix_recognition_records_device_id",
    ):
        op.drop_index(index_name, table_name="recognition_records", if_exists=True)

    op.drop_constraint("fk_personnel_department_id_departments", "personnel", type_="foreignkey")
    op.execute(
        """
        UPDATE personnel
        SET department_id = NULL
        WHERE department_id IS NOT NULL
          AND department_id NOT IN (SELECT id FROM locations)
        """
    )
    op.create_foreign_key(
        "fk_personnel_department_id_locations",
        "personnel",
        "locations",
        ["department_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.drop_index("ix_departments_is_active", table_name="departments")
    op.drop_index("ix_departments_parent_id", table_name="departments")
    op.drop_table("departments")
    WEEKDAY_ENUM.drop(op.get_bind(), checkfirst=True)
