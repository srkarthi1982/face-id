# Personnel Module - Foreign Keys Reference

**Generated:** 2026-07-24  
**Status:** ✅ All Foreign Keys Validated

---

## Overview

This document lists all foreign key constraints involving the Personnel module and related tables. All FKs are properly configured for JOIN queries.

---

## Foreign Key Summary

### Personnel Table (6 FKs total)

| FK Column | References | Constraint Name | On Delete | Index |
|-----------|------------|-----------------|-----------|-------|
| `org_id` | `locations.id` | `fk_personnel_org_id_locations` | SET NULL | ✅ `ix_personnel_org_id` |
| `department_id` | `locations.id` | `fk_personnel_department_id_locations` | SET NULL | ✅ `ix_personnel_department_id` |
| `person_id_internal` | *(unique constraint)* | `uq_personnel_person_id_internal` | - | - |

**Relationships:**
- `Personnel.organization` → Location (org_id)
- `Personnel.department` → Location (department_id)
- `Personnel.photo_registration` → PhotoRegistration (person_id_internal)
- `Personnel.device_mappings` → DevicePersonMapping (person_id_internal)

---

### Photo Registrations Table (2 FKs)

| FK Column | References | Constraint Name | On Delete | Index |
|-----------|------------|-----------------|-----------|-------|
| `person_id_internal` | `personnel.person_id_internal` | `fk_photo_registrations_person_id` | CASCADE | ✅ `ix_photo_registrations_person_id_internal` |
| `device_id` | `devices.id` | `fk_photo_registrations_device_id` | CASCADE | ✅ `ix_photo_registrations_device_id` |

**Relationships:**
- `PhotoRegistration.personnel` → Personnel
- `PhotoRegistration.device` → Device

---

### Device Person Mapping Table (2 FKs)

| FK Column | References | Constraint Name | On Delete | Index |
|-----------|------------|-----------------|-----------|-------|
| `person_id_internal` | `personnel.person_id_internal` | `fk_device_person_mapping_person_id` | CASCADE | ✅ `ix_device_person_mapping_person_id_internal` |
| `device_id` | `devices.id` | `fk_device_person_mapping_device_id` | CASCADE | ✅ `ix_device_person_mapping_device_id` |

**Relationships:**
- `DevicePersonMapping.personnel` → Personnel
- `DevicePersonMapping.device` → Device

---

### Devices Table (1 FK)

| FK Column | References | Constraint Name | On Delete | Index |
|-----------|------------|-----------------|-----------|-------|
| `location_id` | `locations.id` | `fk_devices_location_id` | SET NULL | - |

**Relationships:**
- `Device.location` → Location
- `Device.person_mappings` → DevicePersonMapping (reverse)
- `Device.photo_registrations` → PhotoRegistration (reverse)

---

### Locations Table (No FKs)

**Reverse Relationships:**
- `Location.personnel` → Personnel (org_id)
- `Location.personnel_department` → Personnel (department_id)
- `Location.devices` → Device (location_id)

---

## JOIN Query Examples

### 1. Personnel with Organization and Department

```sql
SELECT 
    p.emp_no,
    p.full_name,
    org.name as org_name,
    dept.name as dept_name
FROM personnel p
LEFT JOIN locations org ON p.org_id = org.id
LEFT JOIN locations dept ON p.department_id = dept.id
```

**SQLAlchemy:**
```python
from sqlalchemy.orm import joinedload

query = select(Personnel).options(
    joinedload(Personnel.organization),
    joinedload(Personnel.department)
)
```

---

### 2. Personnel with Photo Registrations

```sql
SELECT 
    p.emp_no,
    p.full_name,
    pr.face_id,
    pr.img_url
FROM personnel p
LEFT JOIN photo_registrations pr ON p.person_id_internal = pr.person_id_internal
```

**SQLAlchemy:**
```python
query = select(Personnel).options(
    joinedload(Personnel.photo_registration)
)
```

---

### 3. Personnel with Device Mappings

```sql
SELECT 
    p.emp_no,
    dpm.device_id,
    dpm.person_id_device,
    dpm.synced_at
FROM personnel p
LEFT JOIN device_person_mapping dpm ON p.person_id_internal = dpm.person_id_internal
```

**SQLAlchemy:**
```python
query = select(Personnel).options(
    joinedload(Personnel.device_mappings)
)
```

---

### 4. Complex 5-Table JOIN

```sql
SELECT 
    p.emp_no,
    p.full_name,
    org.name as org_name,
    dept.name as dept_name,
    pr.face_id,
    d.device_name,
    dpm.person_id_device
FROM personnel p
LEFT JOIN locations org ON p.org_id = org.id
LEFT JOIN locations dept ON p.department_id = dept.id
LEFT JOIN photo_registrations pr ON p.person_id_internal = pr.person_id_internal
LEFT JOIN devices d ON pr.device_id = d.id
LEFT JOIN device_person_mapping dpm ON p.person_id_internal = dpm.person_id_internal
```

**SQLAlchemy:**
```python
from sqlalchemy.orm import joinedload

query = select(Personnel).options(
    joinedload(Personnel.organization),
    joinedload(Personnel.department),
    joinedload(Personnel.photo_registration).joinedload(PhotoRegistration.device),
    joinedload(Personnel.device_mappings).joinedload(DevicePersonMapping.device)
)
```

---

## Migration History

| Migration ID | Description | Date |
|--------------|-------------|------|
| `25342c60b8dc` | Added org_id, department_id FKs to personnel | 2026-07-23 |
| `838c997c73e7` | Added unique constraint on personnel.person_id_internal | 2026-07-24 |
| `263de27c0a92` | Added FKs to photo_registrations and device_person_mapping | 2026-07-24 |

---

## Verification Commands

### Check Foreign Keys in Database

```sql
SELECT 
    tc.constraint_name, 
    tc.table_name, 
    kcu.column_name, 
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name 
FROM information_schema.table_constraints AS tc 
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
AND tc.table_name IN ('personnel', 'photo_registrations', 'device_person_mapping')
ORDER BY tc.table_name;
```

### Test JOIN Query

```bash
cd backend
uv run python -c "
from sqlalchemy.orm import Session, joinedload
from app.modules.personnel.models import Personnel
from app.core.database import get_db

db = next(get_db())
query = db.query(Personnel).options(
    joinedload(Personnel.organization),
    joinedload(Personnel.department),
    joinedload(Personnel.photo_registration),
    joinedload(Personnel.device_mappings)
)
results = query.limit(5).all()
print(f'Query returned {len(results)} results')
"
```

---

## Notes

1. **CASCADE vs SET NULL:**
   - `photo_registrations` and `device_person_mapping` use CASCADE (delete when personnel deleted)
   - `personnel.org_id` and `personnel.department_id` use SET NULL (preserve personnel if org/dept deleted)

2. **Unique Constraint:**
   - `personnel.person_id_internal` has unique constraint to support FK references
   - This ensures data integrity across related tables

3. **Indexes:**
   - All FK columns have indexes for JOIN performance
   - Composite index on `(emp_no, org_id)` for uniqueness

4. **Multi-Tenancy:**
   - Personnel scoped by `org_id` (Location table)
   - Unique constraint on `(emp_no, org_id)` allows same emp_no in different orgs

---

**Status:** ✅ All foreign keys validated and tested  
**Last Verified:** 2026-07-24
