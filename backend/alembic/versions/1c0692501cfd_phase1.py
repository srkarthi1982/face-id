"""phase1 devices personnel photos records

Revision ID: 1c0692501cfd_phase1
Revises: ddb65fd1e152_initial_data
Create Date: 2026-07-16

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "1c0692501cfd"
down_revision: Union[str, None] = "ddb65fd1e152"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create devices table
    op.create_table(
        "devices",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("device_id", sa.String(length=64), nullable=False),
        sa.Column("device_name", sa.String(length=200), nullable=False),
        sa.Column("ip_address", sa.String(length=45), nullable=False),
        sa.Column("port", sa.Integer(), nullable=False),
        sa.Column("api_password", sa.String(length=255), nullable=False),
        sa.Column("serial_number", sa.String(length=200), nullable=True),
        sa.Column("firmware_version", sa.String(length=100), nullable=True),
        sa.Column("sdk_version", sa.String(length=100), nullable=True),
        sa.Column("location", sa.String(length=200), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("settings", sa.JSON(), server_default="{}", nullable=False),
        sa.Column("callback_urls", sa.JSON(), server_default="{}", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("device_id"),
    )

    # Create personnel table
    op.create_table(
        "personnel",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("person_id_internal", sa.String(length=64), nullable=False),
        sa.Column("person_id_device", sa.String(length=64), nullable=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("card_no", sa.String(length=100), nullable=True),
        sa.Column("idcard_num", sa.String(length=50), nullable=True),
        sa.Column("id_number", sa.String(length=50), nullable=True),
        sa.Column("permissions", sa.JSON(), server_default="{}", nullable=False),
        sa.Column("pass_time", sa.JSON(), nullable=True),
        sa.Column("push_to_device", sa.Boolean(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create photo_registrations table
    op.create_table(
        "photo_registrations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("person_id_internal", sa.String(length=64), nullable=False),
        sa.Column("person_id_device", sa.String(length=64), nullable=True),
        sa.Column("device_id", sa.Integer(), nullable=False),
        sa.Column("face_id", sa.String(length=64), nullable=True),
        sa.Column("feature", sa.String(length=100), nullable=True),
        sa.Column("feature_key", sa.String(length=100), nullable=True),
        sa.Column("img_url", sa.String(length=500), nullable=True),
        sa.Column("img_data", sa.LargeBinary(), nullable=True),
        sa.Column("source", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create recognition_records table
    op.create_table(
        "recognition_records",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("device_id", sa.Integer(), nullable=False),
        sa.Column("person_id_internal", sa.String(length=64), nullable=True),
        sa.Column("person_id_device", sa.String(length=64), nullable=True),
        sa.Column("record_type", sa.String(length=30), nullable=False),
        sa.Column("mode", sa.String(length=50), nullable=True),
        sa.Column("event_type", sa.String(length=20), nullable=True),
        sa.Column("event_name", sa.String(length=50), nullable=True),
        sa.Column("event_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("img_data", sa.LargeBinary(), nullable=True),
        sa.Column("source", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create callback_configs table
    op.create_table(
        "callback_configs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("device_id", sa.Integer(), nullable=False),
        sa.Column("config_type", sa.String(length=50), nullable=False),
        sa.Column("callback_url", sa.String(length=500), nullable=True),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create device_person_mapping table
    op.create_table(
        "device_person_mapping",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("person_id_internal", sa.String(length=64), nullable=False),
        sa.Column("device_id", sa.Integer(), nullable=False),
        sa.Column("person_id_device", sa.String(length=64), nullable=True),
        sa.Column("photo_ids", sa.JSON(), server_default="{}", nullable=False),
        sa.Column("synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("device_person_mapping")
    op.drop_table("callback_configs")
    op.drop_table("recognition_records")
    op.drop_table("photo_registrations")
    op.drop_table("personnel")
    op.drop_table("devices")
