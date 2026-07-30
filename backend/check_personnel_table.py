from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
result = db.execute(text("""
    SELECT column_name, data_type, is_nullable, column_default
    FROM information_schema.columns
    WHERE table_name = 'personnel'
    ORDER BY ordinal_position
"""))
print("Personnel table columns:")
for row in result:
    print(f"  {row.column_name}: {row.data_type} (nullable={row.is_nullable}, default={row.column_default})")

# Check constraints
result2 = db.execute(text("""
    SELECT conname, contype, conkey
    FROM pg_constraint
    WHERE conrelid = 'personnel'::regclass
"""))
print("\nConstraints:")
for row in result2:
    print(f"  {row.conname}: {row.contype}")

db.close()
