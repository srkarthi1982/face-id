# Backend Agent Instructions - Personnel Module

## Context
You are assisting the backend developer implementing the Personnel module for the JAC Face ID Management System.

## Implementation Plan
**Primary Reference:** `.opencode/plans/personnel-module-implementation.md`

## Before Starting Each Session
1. Read `.opencode/progress-log.md` to see current status
2. Check latest git commits: `git log -5 --oneline`
3. Review `backend/app/modules/personnel/` for current state
4. Identify which Track to work on (1.1 → 1.2 → 1.3 → 1.4 → 1.5)

## During Session
1. Follow the implementation plan tracks in order
2. Commit every 30-60 minutes with structured messages
3. Run tests after completing each track
4. Update progress log when completing tracks
5. **CRITICAL: After ANY model change, verify foreign keys for JOIN queries** (see "Foreign Key Validation Protocol" below)

## Git Commit Message Format
```
personnel: [Track X.X] <description>
<details>

Progress: Day X/10 - Backend Track X.X <STATUS>
```

**Example:**
```
personnel: [Track 1.1] Define Personnel model
- Add all 15 required fields from specification
- Add relationships to Organization, PhotoRegistration, DevicePersonMapping
- Create unique constraint uq_personnel_emp_no_org
- Add indexes on org_id, emp_no, is_active

Progress: Day 1/10 - Backend Track 1.1 COMPLETE ✅
```

## After Each Session
1. Commit all work (even if incomplete - use "WIP:" prefix)
2. Update `.opencode/progress-log.md` with:
   - Track number and status
   - What was completed
   - Files modified
   - Any blockers
   - Next session plan
3. Leave notes in session file if mid-track

## Session File Template
Create: `.opencode/sessions/backend-YYYY-MM-DD.md`
```markdown
# Backend Session - YYYY-MM-DD
**Developer:** [Name]
**Track:** X.X - <Track Name>
**Status:** COMPLETE / IN PROGRESS / BLOCKED

## Goal
<What you planned to accomplish>

## Completed
- [ ] Task 1
- [ ] Task 2

## Files Modified
- `backend/app/modules/personnel/file.py`

## Issues/Blockers
<Any issues encountered>

## Next Session
<What to work on next>
```

## Testing Commands
```bash
# Check model imports
cd backend
uv run python -c "from app.modules.personnel.models import Personnel; print('Model OK')"

# Test migration
uv run alembic current
uv run alembic upgrade head
uv run alembic downgrade -1

# Start server for testing
uv run uvicorn app.main:app --reload --port 8000

# Verify foreign keys (CRITICAL after model changes)
uv run python scripts/verify-foreign-keys.py
```

## Key Files Reference
- Model: `backend/app/modules/personnel/models.py`
- Service: `backend/app/modules/personnel/service.py`
- Router: `backend/app/modules/personnel/router.py`
- Schemas: `backend/app/modules/personnel/schemas.py`
- Permissions: `backend/app/core/permissions.py`
- Migration: `backend/alembic/versions/*.py`

## Integration Points
- Organization FK → `backend/app/modules/master/models.py`
- Photo Registration → `backend/app/modules/photos/models.py`
- Device Mapping → `backend/app/modules/person_mapping/models.py`

## When Blocked
1. Check existing modules for patterns (e.g., `device/`, `users/`)
2. Review `backend/app/core/database.py` for SQLAlchemy setup
3. Consult progress log for frontend developer status
4. Ask for clarification via developer

---

## Foreign Key Validation Protocol ⚠️ CRITICAL

**When to Run:** After ANY change to model files (`models.py`) in:
- `backend/app/modules/personnel/`
- `backend/app/modules/photos/`
- `backend/app/modules/person_mapping/`
- `backend/app/modules/device/`
- `backend/app/modules/master/`

### Step 1: Verify Model Relationships

Check that all relationships have proper `ForeignKey()` declarations:

```python
# ✅ GOOD - Has ForeignKey
person_id_internal: Mapped[str] = mapped_column(
    String(64),
    ForeignKey("personnel.person_id_internal", ondelete="CASCADE"),
    nullable=False,
    index=True
)

# ❌ BAD - Missing ForeignKey
person_id_internal: Mapped[str] = mapped_column(String(64), nullable=False)
```

**Checklist:**
- [ ] All FK columns have `ForeignKey()` constraint
- [ ] All FK columns have `index=True` for performance
- [ ] All FK columns have proper `ondelete` behavior (CASCADE or SET NULL)
- [ ] Both sides of relationship are defined (e.g., `Personnel.photo_registration` AND `PhotoRegistration.personnel`)
- [ ] `foreign_keys=[...]` specified when multiple paths exist
- [ ] `back_populates` matches on both sides

### Step 2: Generate Migration

```bash
cd backend
uv run alembic revision --autogenerate -m "add_missing_fks_<table_name>"
```

**Verify migration includes:**
- [ ] `op.create_foreign_key()` for each new FK
- [ ] `op.create_index()` for each FK column
- [ ] Proper constraint names (e.g., `fk_<table>_<column>`)

### Step 3: Apply & Test Migration

```bash
# Apply migration
uv run alembic upgrade head

# Verify FKs in database
uv run python -c "
from sqlalchemy import create_engine, text
from app.core.config import settings

engine = create_engine(str(settings.DATABASE_URL))
with engine.connect() as conn:
    result = conn.execute(text('''
        SELECT tc.table_name, kcu.column_name, 
               ccu.table_name AS foreign_table,
               ccu.column_name AS foreign_column,
               tc.constraint_name
        FROM information_schema.table_constraints AS tc 
        JOIN information_schema.key_column_usage AS kcu
            ON tc.constraint_name = kcu.constraint_name
        JOIN information_schema.constraint_column_usage AS ccu
            ON ccu.constraint_name = tc.constraint_name
        WHERE tc.constraint_type = 'FOREIGN KEY'
        AND tc.table_name IN ('personnel', 'photo_registrations', 'device_person_mapping')
        ORDER BY tc.table_name
    '''))
    for row in result:
        print(f'{row.table_name}.{row.column_name} -> {row.foreign_table}.{row.foreign_column}')
"
```

### Step 4: Test JOIN Query

```bash
cd backend
uv run python -c "
from sqlalchemy.orm import Session, joinedload
from app.modules.personnel.models import Personnel
from app.modules.photos.models import PhotoRegistration
from app.modules.person_mapping.models import DevicePersonMapping
from app.modules.device.models import Device
from app.core.database import get_db

db = next(get_db())

# Test complex JOIN
query = db.query(Personnel).options(
    joinedload(Personnel.organization),
    joinedload(Personnel.department),
    joinedload(Personnel.photo_registration).joinedload(PhotoRegistration.device),
    joinedload(Personnel.device_mappings).joinedload(DevicePersonMapping.device)
)

results = query.limit(1).all()
print(f'✅ JOIN query successful - returned {len(results)} results')
"
```

### Step 5: Common Issues & Fixes

| Issue | Error | Fix |
|-------|-------|-----|
| Missing unique constraint | `there is no unique constraint matching given keys` | Add `UniqueConstraint` or `unique=True` to referenced column |
| Missing index | Slow JOIN performance | Add `index=True` to FK column |
| Circular dependency | `Circular dependency detected` | Use `foreign_keys=[...]` to disambiguate |
| Missing back_populates | Warning in logs | Add `back_populates` on both sides |
| Wrong table name | `Table 'x' not found` | Check table name in `__tablename__` |

### Step 6: Update Documentation

After verifying FKs, update:
- [ ] `.opencode/foreign-keys-reference.md` with new FKs
- [ ] `.opencode/progress-log.md` with validation status
- [ ] Session file with FK validation results

---

## Quick Reference: Foreign Key Patterns

### One-to-Many (Parent → Child)

```python
# Parent model
class Personnel(Base):
    # ...
    device_mappings: Mapped[list["DevicePersonMapping"]] = relationship(
        back_populates="personnel"
    )

# Child model
class DevicePersonMapping(Base):
    person_id_internal: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("personnel.person_id_internal", ondelete="CASCADE"),
        index=True
    )
    personnel: Mapped["Personnel"] = relationship(
        back_populates="device_mappings"
    )
```

### One-to-One (with unique FK)

```python
# Parent
class Personnel(Base):
    photo_registration: Mapped[Optional["PhotoRegistration"]] = relationship(
        back_populates="personnel",
        uselist=False
    )

# Child (with unique FK)
class PhotoRegistration(Base):
    person_id_internal: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("personnel.person_id_internal", ondelete="CASCADE"),
        unique=True,  # Makes it one-to-one
        index=True
    )
    personnel: Mapped["Personnel"] = relationship(
        back_populates="photo_registration"
    )
```

### Self-Referential (Hierarchy)

```python
class Location(Base):
    parent_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("locations.id")
    )
    parent: Mapped[Optional["Location"]] = relationship(
        foreign_keys=[parent_id],
        remote_side=[parent_id]
    )
    children: Mapped[list["Location"]] = relationship(
        foreign_keys=[parent_id]
    )
```

### Multiple Paths to Same Table

```python
class Personnel(Base):
    # Two FKs to same table (locations)
    org_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("locations.id"),
        index=True
    )
    department_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("locations.id"),
        index=True
    )
    
    # Must specify foreign_keys explicitly
    organization: Mapped[Optional["Location"]] = relationship(
        foreign_keys=[org_id],
        back_populates="personnel"
    )
    department: Mapped[Optional["Location"]] = relationship(
        foreign_keys=[department_id],
        back_populates="personnel_department"
    )

# Location must define both relationships
class Location(Base):
    personnel: Mapped[list["Personnel"]] = relationship(
        back_populates="organization",
        foreign_keys="Personnel.org_id"
    )
    personnel_department: Mapped[list["Personnel"]] = relationship(
        back_populates="department",
        foreign_keys="Personnel.department_id"
    )
```

---

## Migration Best Practices

1. **Always test upgrade AND downgrade:**
   ```bash
   uv run alembic upgrade head
   uv run alembic downgrade -1  # Verify rollback
   uv run alembic upgrade head  # Re-apply
   ```

2. **Name constraints explicitly:**
   ```python
   op.create_foreign_key(
       'fk_photo_registrations_person_id',  # Explicit name
       'photo_registrations', 'personnel',
       ['person_id_internal'], ['person_id_internal'],
       ondelete='CASCADE'
   )
   ```

3. **Add indexes for all FKs:**
   ```python
   op.create_index(
       'ix_photo_registrations_person_id_internal',
       'photo_registrations',
       ['person_id_internal'],
       unique=False
   )
   ```

4. **Document in migration:**
   ```python
   def upgrade() -> None:
       # Add FK to personnel.person_id_internal
       # Required for JOIN queries in service layer
       op.create_foreign_key(...)
   ```

---

## Related Documentation

- **FK Reference:** `.opencode/foreign-keys-reference.md` - Complete FK listing with examples
- **Implementation Plan:** `.opencode/plans/personnel-module-implementation.md` - Track details
- **Progress Log:** `.opencode/progress-log.md` - Current status
- **Session Files:** `.opencode/sessions/backend-*.md` - Daily logs
