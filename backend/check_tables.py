from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
result = db.execute(text("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    ORDER BY table_name
"""))
print("Tables in database:")
for row in result:
    print(f"  {row[0]}")
db.close()
