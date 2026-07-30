#!/usr/bin/env python
"""
Verify Foreign Keys for Personnel Module

This script validates that all foreign key constraints are properly defined
and that JOIN queries work correctly across related tables.

Usage:
    cd backend
    uv run python scripts/verify-foreign-keys.py

Run this script:
- After ANY model change in personnel, photos, person_mapping, device, or master modules
- Before committing model changes
- When debugging JOIN query issues
"""

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import create_engine, text, inspect
from app.core.config import settings
from app.modules.personnel.models import Personnel
from app.modules.photos.models import PhotoRegistration
from app.modules.person_mapping.models import DevicePersonMapping
from app.modules.device.models import Device
from app.modules.master.models import Location


def print_header(text: str):
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80)


def status_ok():
    return "[OK]"


def status_fail():
    return "[FAIL]"


def status_warn():
    return "[WARN]"


def check_foreign_keys():
    """Verify all expected foreign keys exist in database."""
    print_header("CHECKING FOREIGN KEYS")
    
    engine = create_engine(str(settings.DATABASE_URL))
    inspector = inspect(engine)
    
    expected_fks = {
        'personnel': [
            ('org_id', 'locations', 'id'),
            ('department_id', 'locations', 'id'),
        ],
        'photo_registrations': [
            ('person_id_internal', 'personnel', 'person_id_internal'),
            ('device_id', 'devices', 'id'),
        ],
        'device_person_mapping': [
            ('person_id_internal', 'personnel', 'person_id_internal'),
            ('device_id', 'devices', 'id'),
        ],
        'devices': [
            ('location_id', 'locations', 'id'),
        ],
    }
    
    all_ok = True
    
    for table_name, expected_fks_for_table in expected_fks.items():
        print(f"\nTable: {table_name}")
        
        try:
            fks = inspector.get_foreign_keys(table_name)
            existing_fks = [
                (fk['constrained_columns'][0], 
                 fk['referred_table'], 
                 fk['referred_columns'][0])
                for fk in fks
            ]
            
            for col, ref_table, ref_col in expected_fks_for_table:
                if (col, ref_table, ref_col) in existing_fks:
                    print(f"  {status_ok()} {col} -> {ref_table}.{ref_col}")
                else:
                    print(f"  {status_fail()} MISSING: {col} -> {ref_table}.{ref_col}")
                    all_ok = False
            
            # Show any unexpected FKs
            for col, ref_table, ref_col in existing_fks:
                if (col, ref_table, ref_col) not in expected_fks_for_table:
                    print(f"  {status_warn()} UNEXPECTED: {col} -> {ref_table}.{ref_col}")
                    
        except Exception as e:
            print(f"  {status_fail()} ERROR: {e}")
            all_ok = False
    
    return all_ok


def check_indexes():
    """Verify indexes exist on all foreign key columns."""
    print_header("CHECKING INDEXES")
    
    engine = create_engine(str(settings.DATABASE_URL))
    inspector = inspect(engine)
    
    expected_indexes = {
        'personnel': ['org_id', 'department_id', 'emp_no', 'is_active'],
        'photo_registrations': ['person_id_internal', 'device_id'],
        'device_person_mapping': ['person_id_internal', 'device_id'],
    }
    
    all_ok = True
    
    for table_name, expected_cols in expected_indexes.items():
        print(f"\nTable: {table_name}")
        
        try:
            indexes = inspector.get_indexes(table_name)
            indexed_cols = set()
            for idx in indexes:
                indexed_cols.update(idx['column_names'])
            
            for col in expected_cols:
                if col in indexed_cols:
                    print(f"  {status_ok()} Index on {col}")
                else:
                    print(f"  {status_fail()} MISSING INDEX: {col}")
                    all_ok = False
                    
        except Exception as e:
            print(f"  {status_fail()} ERROR: {e}")
            all_ok = False
    
    return all_ok


def check_unique_constraints():
    """Verify unique constraints required for FK references."""
    print_header("CHECKING UNIQUE CONSTRAINTS")
    
    engine = create_engine(str(settings.DATABASE_URL))
    inspector = inspect(engine)
    
    expected_unique = {
        'personnel': ['person_id_internal', ('emp_no', 'org_id')],
    }
    
    all_ok = True
    
    for table_name, expected_cols in expected_unique.items():
        print(f"\nTable: {table_name}")
        
        try:
            uniques = inspector.get_unique_constraints(table_name)
            unique_cols = set()
            for u in uniques:
                if isinstance(u['column_names'], list):
                    if len(u['column_names']) == 1:
                        unique_cols.add(u['column_names'][0])
                    else:
                        unique_cols.add(tuple(u['column_names']))
            
            for col in expected_cols:
                if col in unique_cols:
                    print(f"  {status_ok()} Unique constraint: {col}")
                else:
                    print(f"  {status_fail()} MISSING UNIQUE: {col}")
                    all_ok = False
                    
        except Exception as e:
            print(f"  {status_fail()} ERROR: {e}")
            all_ok = False
    
    return all_ok


def check_indexes():
    """Verify indexes exist on all foreign key columns."""
    print_header("CHECKING INDEXES")
    
    engine = create_engine(str(settings.DATABASE_URL))
    inspector = inspect(engine)
    
    expected_indexes = {
        'personnel': ['org_id', 'department_id', 'emp_no', 'is_active'],
        'photo_registrations': ['person_id_internal', 'device_id'],
        'device_person_mapping': ['person_id_internal', 'device_id'],
    }
    
    all_ok = True
    
    for table_name, expected_cols in expected_indexes.items():
        print(f"\nTable: {table_name}")
        
        try:
            indexes = inspector.get_indexes(table_name)
            indexed_cols = set()
            for idx in indexes:
                indexed_cols.update(idx['column_names'])
            
            for col in expected_cols:
                if col in indexed_cols:
                    print(f"  {status_ok()} Index on {col}")
                else:
                    print(f"  {status_fail()} MISSING INDEX: {col}")
                    all_ok = False
                    
        except Exception as e:
            print(f"  {status_fail()} ERROR: {e}")
            all_ok = False
    
    return all_ok


def check_unique_constraints():
    """Verify unique constraints required for FK references."""
    print_header("CHECKING UNIQUE CONSTRAINTS")
    
    engine = create_engine(str(settings.DATABASE_URL))
    inspector = inspect(engine)
    
    expected_unique = {
        'personnel': ['person_id_internal', ('emp_no', 'org_id')],
    }
    
    all_ok = True
    
    for table_name, expected_cols in expected_unique.items():
        print(f"\nTable: {table_name}")
        
        try:
            uniques = inspector.get_unique_constraints(table_name)
            unique_cols = set()
            for u in uniques:
                if isinstance(u['column_names'], list):
                    if len(u['column_names']) == 1:
                        unique_cols.add(u['column_names'][0])
                    else:
                        unique_cols.add(tuple(u['column_names']))
            
            for col in expected_cols:
                if col in unique_cols:
                    print(f"  {status_ok()} Unique constraint: {col}")
                else:
                    print(f"  {status_fail()} MISSING UNIQUE: {col}")
                    all_ok = False
                    
        except Exception as e:
            print(f"  {status_fail()} ERROR: {e}")
            all_ok = False
    
    return all_ok


def test_join_query():
    """Test a complex JOIN query across all related tables."""
    print_header("TESTING JOIN QUERY")
    
    engine = create_engine(str(settings.DATABASE_URL))
    
    query = text("""
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
        LIMIT 5
    """)
    
    try:
        with engine.connect() as conn:
            result = conn.execute(query)
            rows = result.fetchall()
            
        print(f"\n{status_ok()} JOIN query executed successfully")
        print(f"   Returned {len(rows)} rows")
        
        if rows:
            print("\n   Sample data:")
            for row in rows[:3]:
                print(f"   - {row.emp_no}: {row.full_name} ({row.org_name})")
                
        return True
        
    except Exception as e:
        print(f"\n{status_fail()} JOIN query FAILED: {e}")
        return False


def check_model_relationships():
    """Verify SQLAlchemy relationships are properly defined."""
    print_header("CHECKING MODEL RELATIONSHIPS")
    
    checks = [
        (Personnel, 'organization', 'org_id -> locations.id'),
        (Personnel, 'department', 'department_id -> locations.id'),
        (Personnel, 'photo_registrations', 'person_id_internal'),
        (Personnel, 'device_mappings', 'person_id_internal'),
        (PhotoRegistration, 'personnel', 'person_id_internal'),
        (PhotoRegistration, 'device', 'device_id'),
        (DevicePersonMapping, 'personnel', 'person_id_internal'),
        (DevicePersonMapping, 'device', 'device_id'),
        (Device, 'location', 'location_id'),
        (Device, 'person_mappings', 'reverse'),
        (Device, 'photo_registrations', 'reverse'),
        (Location, 'personnel', 'reverse org_id'),
        (Location, 'personnel_department', 'reverse department_id'),
    ]
    
    all_ok = True
    
    for model_class, relationship_name, description in checks:
        try:
            rel = getattr(model_class, relationship_name)
            print(f"  {status_ok()} {model_class.__name__}.{relationship_name} ({description})")
        except AttributeError:
            print(f"  {status_fail()} MISSING: {model_class.__name__}.{relationship_name}")
            all_ok = False
    
    return all_ok


def main():
    """Run all verification checks."""
    print("\n" + "=" * 80)
    print("  FOREIGN KEY VALIDATION - Personnel Module")
    print("=" * 80)
    
    results = []
    
    # Run all checks
    results.append(("Model Relationships", check_model_relationships()))
    results.append(("Foreign Keys", check_foreign_keys()))
    results.append(("Indexes", check_indexes()))
    results.append(("Unique Constraints", check_unique_constraints()))
    results.append(("JOIN Query", test_join_query()))
    
    # Summary
    print_header("SUMMARY")
    
    all_passed = True
    for check_name, passed in results:
        result_str = "PASS" if passed else "FAIL"
        print(f"[{result_str}] {check_name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 80)
    
    if all_passed:
        print("[OK] ALL CHECKS PASSED - Foreign keys are valid for JOIN queries")
        return 0
    else:
        print("[FAIL] SOME CHECKS FAILED - Review issues above")
        print("\n[WARN] Do not commit model changes until all FK issues are resolved!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
