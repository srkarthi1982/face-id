"""Explicit SQLAlchemy Core declarations for the external Luna contract."""

from sqlalchemy import (
    BigInteger,
    Column,
    Date,
    DateTime,
    Identity,
    Integer,
    MetaData,
    SmallInteger,
    String,
    Table,
)


luna_metadata = MetaData()

saas_ca_person = Table(
    "saas_ca_person",
    luna_metadata,
    Column("id", BigInteger, Identity(start=1, increment=1), primary_key=True, nullable=False),
    Column("org_id", String(64), nullable=True),
    Column("person_id", String(64), nullable=True),
    Column("person_no", String(64), nullable=True),
    Column("person_name", String(200), nullable=True),
    Column("del_status", SmallInteger, nullable=False),
    Column("gmt_modified", DateTime(timezone=False), nullable=True),
    Column("gmt_create", DateTime(timezone=False), nullable=True),
    schema="dbo",
)

saas_ca_clock_record = Table(
    "saas_ca_clock_record",
    luna_metadata,
    Column("id", BigInteger, Identity(start=1, increment=1), primary_key=True, nullable=False),
    Column("org_id", String(64), nullable=True),
    Column("record_id", String(64), nullable=True),
    Column("person_id", String(64), nullable=True),
    Column("person_no", String(64), nullable=True),
    Column("photo_id", String(64), nullable=True),
    Column("photo_url", String(255), nullable=True),
    Column("device_key", String(64), nullable=True),
    Column("recognition_time", BigInteger, nullable=True),
    Column("fix_status", SmallInteger, nullable=True),
    Column("del_status", SmallInteger, nullable=False),
    Column("gmt_modified", DateTime(timezone=False), nullable=True),
    Column("gmt_create", DateTime(timezone=False), nullable=True),
    Column("clock_type", Integer, nullable=True),
    Column("person_name", String(255), nullable=True),
    Column("device_name", String(255), nullable=True),
    schema="dbo",
)

saas_ca_report_daily = Table(
    "saas_ca_report_daily",
    luna_metadata,
    Column("id", BigInteger, Identity(start=1, increment=1), primary_key=True, nullable=False),
    Column("org_id", String(64), nullable=True),
    Column("report_date", Date, nullable=True),
    Column("person_id", String(64), nullable=True),
    Column("person_no", String(64), nullable=True),
    Column("person_name", String(255), nullable=True),
    Column("dept_name", String(255), nullable=True),
    Column("interval_id", BigInteger, nullable=True),
    Column("interval_name", String(255), nullable=True),
    Column("plan_sign_in_datetime", DateTime(timezone=False), nullable=True),
    Column("plan_sign_out_datetime", DateTime(timezone=False), nullable=True),
    Column("plan_work_time", BigInteger, nullable=True),
    Column("clock_sign_in_datetime", DateTime(timezone=False), nullable=True),
    Column("clock_sign_in_status", SmallInteger, nullable=True),
    Column("clock_sign_out_datetime", DateTime(timezone=False), nullable=True),
    Column("clock_sign_out_status", SmallInteger, nullable=True),
    Column("real_work_time", BigInteger, nullable=True),
    Column("normal_time", BigInteger, nullable=True),
    Column("late_time", BigInteger, nullable=True),
    Column("early_time", BigInteger, nullable=True),
    Column("absent_time", BigInteger, nullable=True),
    Column("sign_start_time", DateTime(timezone=False), nullable=True),
    Column("sign_end_time", DateTime(timezone=False), nullable=True),
    Column("overwork_time", BigInteger, nullable=True),
    Column("date_type", SmallInteger, nullable=True),
    Column("del_status", SmallInteger, nullable=False),
    Column("gmt_modified", DateTime(timezone=False), nullable=True),
    Column("gmt_create", DateTime(timezone=False), nullable=True),
    schema="dbo",
)

saas_ca_report_exception = Table(
    "saas_ca_report_exception",
    luna_metadata,
    Column("id", BigInteger, Identity(start=1, increment=1), primary_key=True, nullable=False),
    Column("org_id", String(64), nullable=True),
    Column("person_id", String(64), nullable=True),
    Column("report_date", Date, nullable=True),
    Column("clock_time", DateTime(timezone=False), nullable=True),
    Column("clock_photo_id", String(256), nullable=True),
    Column("device_key", String(64), nullable=True),
    Column("device_name", String(128), nullable=True),
    Column("del_status", SmallInteger, nullable=False),
    Column("gmt_modified", DateTime(timezone=False), nullable=True),
    Column("gmt_create", DateTime(timezone=False), nullable=True),
    schema="dbo",
)

APPROVED_LUNA_TABLES = frozenset(
    {
        "saas_ca_person",
        "saas_ca_clock_record",
        "saas_ca_report_daily",
        "saas_ca_report_exception",
    }
)
