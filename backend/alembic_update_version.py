from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
db.execute(text("UPDATE alembic_version SET version_num = '5a35db8d8ed5'"))
db.commit()
db.close()
print("Updated alembic_version to 5a35db8d8ed5")
