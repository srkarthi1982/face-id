from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
result = db.execute(text("SELECT * FROM alembic_version"))
print("Current alembic_version rows:")
for row in result:
    print(f"  {row}")
db.close()
