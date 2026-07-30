from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
db.execute(text("DELETE FROM alembic_version"))
db.execute(text("INSERT INTO alembic_version (version_num) VALUES ('5a35db8d8ed5')"))
db.commit()
db.close()
print("Reset alembic_version to 5a35db8d8ed5 (head)")
