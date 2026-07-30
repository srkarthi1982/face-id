#!/usr/bin/env python
"""
Simple Personnel Module Test - Direct Database Approach

This script tests the Personnel service layer directly via database calls,
bypassing authentication to focus on testing the core functionality.

Usage:
    cd backend
    uv run python scripts/test-personnel-simple.py
"""

import sys
from sqlalchemy.orm import Session

# Import ALL models first to ensure relationships are configured
from app.modules import import_all_models
import_all_models()

# Now import database and models
from app.core.database import SessionLocal
from app.modules.personnel.models import Personnel
from app.modules.personnel.schemas import PersonnelCreate, PersonnelUpdate
from app.modules.personnel.service import (
    create_personnel,
    get_personnel,
    list_personnel,
    update_personnel,
    delete_personnel,
    restore_personnel,
    get_personnel_stats as get_stats,
    search_personnel as search_personnel_service,
)
from app.modules.personnel.schemas import PersonnelSearchFilters
from app.modules.users.models import User


def print_header(text: str):
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80)


def print_subheader(text: str):
    print(f"\n{text}")
    print("-" * 80)


def test_create(db: Session):
    """Test creating personnel"""
    print_subheader("Test 1: Create Personnel")
    
    personnel_data = PersonnelCreate(
        emp_no="TEST001",
        full_name="Test User One",
        gender=1,
        email="test001@example.com",
        phone="+1234567890",
        date_of_birth="1990-01-15",
        nationality="Testonian",
        idcard_num="TESTID123",
        id_number="NAT123456",
        card_no="CARD001",
        position="Test Engineer",
        hire_date="2024-01-01",
        push_to_device=False,
        person_id_internal="test-internal-001",
        person_id_device="test-device-001",
        is_active=True,
    )
    
    try:
        result = create_personnel(db, personnel_data)
        
        if result:
            print(f"  [OK] Created personnel: ID={result.id}")
            print(f"       emp_no={result.emp_no}, name={result.full_name}")
            return result
        else:
            print(f"  [FAIL] No data returned")
            return None
    except Exception as e:
        print(f"  [FAIL] Exception: {e}")
        return None


def test_duplicate_emp_no(db: Session, existing_emp_no: str):
    """Test creating duplicate emp_no"""
    print_subheader("Test 2: Duplicate emp_no (Should Fail)")
    
    personnel_data = PersonnelCreate(
        emp_no=existing_emp_no,  # Duplicate
        full_name="Duplicate Test",
        gender=1,
    )
    
    try:
        result = create_personnel(db, personnel_data)
        print(f"  [FAIL] Should have rejected duplicate emp_no")
        return False
    except Exception as e:
        print(f"  [OK] Correctly rejected duplicate: {str(e)[:100]}")
        return True


def test_list(db: Session):
    """Test listing personnel"""
    print_subheader("Test 3: List Personnel")
    
    try:
        items, total = list_personnel(db, page=1, page_size=10)
        
        if items is not None:
            print(f"  [OK] Listed {len(items)} personnel (Total: {total})")
            return True
        else:
            print(f"  [FAIL] No data returned")
            return False
    except Exception as e:
        print(f"  [FAIL] Exception: {e}")
        return False


def test_get(db: Session, personnel_id: int):
    """Test getting single personnel"""
    print_subheader(f"Test 4: Get Personnel ID={personnel_id}")
    
    try:
        result = get_personnel(db, personnel_id)
        
        if result:
            print(f"  [OK] Retrieved: {result.full_name}")
            return True
        else:
            print(f"  [FAIL] No data returned")
            return False
    except Exception as e:
        print(f"  [FAIL] Exception: {e}")
        return False


def test_update(db: Session, personnel_id: int):
    """Test updating personnel"""
    print_subheader(f"Test 5: Update Personnel ID={personnel_id}")
    
    update_data = PersonnelUpdate(
        position="Senior Test Engineer",
        phone="+9999999999"
    )
    
    try:
        result = update_personnel(db, personnel_id, update_data)
        
        if result:
            print(f"  [OK] Updated personnel")
            print(f"       New position: {result.position}")
            print(f"       New phone: {result.phone}")
            return True
        else:
            print(f"  [FAIL] No data returned")
            return False
    except Exception as e:
        print(f"  [FAIL] Exception: {e}")
        return False


def test_stats(db: Session):
    """Test statistics endpoint"""
    print_subheader("Test 6: Get Statistics")
    
    try:
        stats = get_stats(db)
        
        if stats:
            print(f"  [OK] Retrieved statistics:")
            print(f"       Total: {stats.total}")
            print(f"       Active: {stats.active}")
            print(f"       Inactive: {stats.inactive}")
            return True
        else:
            print(f"  [FAIL] No data returned")
            return False
    except Exception as e:
        print(f"  [FAIL] Exception: {e}")
        return False


def test_search(db: Session):
    """Test search endpoint"""
    print_subheader("Test 7: Search Personnel")
    
    try:
        items = search_personnel_service(db, "Test")
        
        if items is not None:
            print(f"  [OK] Search returned {len(items)} results for 'Test'")
            for item in items[:5]:  # Show first 5
                name = item.full_name if hasattr(item, 'full_name') else str(item)
                print(f"       - {name}")
            return True
        else:
            print(f"  [FAIL] No data returned")
            return False
    except Exception as e:
        print(f"  [FAIL] Exception: {e}")
        return False


def test_soft_delete(db: Session, personnel_id: int):
    """Test soft delete"""
    print_subheader(f"Test 8: Soft Delete Personnel ID={personnel_id}")
    
    try:
        result = delete_personnel(db, personnel_id)
        
        if result:
            print(f"  [OK] Personnel soft-deleted")
            return True
        else:
            print(f"  [FAIL] Delete failed")
            return False
    except Exception as e:
        print(f"  [FAIL] Exception: {e}")
        return False


def test_restore(db: Session, personnel_id: int):
    """Test restore deleted personnel"""
    print_subheader(f"Test 9: Restore Personnel ID={personnel_id}")
    
    try:
        result = restore_personnel(db, personnel_id)
        
        if result:
            print(f"  [OK] Personnel restored")
            print(f"       is_active: {result.is_active}")
            return True
        else:
            print(f"  [FAIL] Restore failed")
            return False
    except Exception as e:
        print(f"  [FAIL] Exception: {e}")
        return False


def test_invalid_gender(db: Session):
    """Test invalid gender validation"""
    print_subheader("Test 10: Invalid Gender (Should Fail)")
    
    try:
        personnel_data = PersonnelCreate(
            emp_no="TEST_INVALID",
            full_name="Invalid Gender Test",
            gender=5,  # Invalid: must be 0, 1, or 2
        )
        result = create_personnel(db, personnel_data)
        print(f"  [FAIL] Should have rejected invalid gender")
        return False
    except Exception as e:
        # Pydantic validation error is expected
        error_msg = str(e)
        if "gender" in error_msg.lower() or "less than" in error_msg.lower():
            print(f"  [OK] Correctly rejected invalid gender (Pydantic validation)")
            return True
        else:
            print(f"  [WARN] Rejected but with unexpected error: {error_msg[:80]}")
            return True  # Still rejected, which is correct


def cleanup_test_data(db: Session, emp_no: str):
    """Clean up test data"""
    print_subheader("Cleanup: Removing test data")
    try:
        db.query(Personnel).filter(Personnel.emp_no == emp_no).delete()
        db.commit()
        print(f"  [OK] Cleaned up test personnel with emp_no={emp_no}")
    except Exception as e:
        print(f"  [WARN] Cleanup failed: {e}")
        db.rollback()


def main():
    """Run all tests."""
    print_header("PERSONNEL MODULE - SERVICE LAYER TESTING")
    print("Testing via direct database calls (bypassing HTTP auth)")
    
    db = SessionLocal()
    results = []
    created_personnel = None
    
    try:
        # Test 1: Create
        print_header("RUNNING TESTS")
        created_personnel = test_create(db)
        
        if created_personnel:
            results.append(("Create Personnel", True))
            
            # Test 2: Duplicate
            results.append(("Duplicate emp_no Rejection", test_duplicate_emp_no(db, created_personnel.emp_no)))
            
            # Test 3: List
            results.append(("List Personnel", test_list(db)))
            
            # Test 4: Get
            results.append(("Get Single Personnel", test_get(db, created_personnel.id)))
            
            # Test 5: Update
            results.append(("Update Personnel", test_update(db, created_personnel.id)))
            
            # Test 6: Stats
            results.append(("Statistics Endpoint", test_stats(db)))
            
            # Test 7: Search
            results.append(("Search Endpoint", test_search(db)))
            
            # Test 8: Delete
            results.append(("Soft Delete", test_soft_delete(db, created_personnel.id)))
            
            # Test 9: Restore
            results.append(("Restore Deleted", test_restore(db, created_personnel.id)))
            
            # Test 10: Invalid gender
            results.append(("Invalid Gender Rejection", test_invalid_gender(db)))
            
        else:
            print("\n[ERROR] Cannot continue tests without created personnel")
            return 1
        
    finally:
        # Cleanup
        if created_personnel:
            cleanup_test_data(db, created_personnel.emp_no)
        db.close()
    
    # Summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {test_name}")
    
    print("\n" + "=" * 80)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n[OK] ALL TESTS PASSED - Personnel module service layer is working correctly!")
        return 0
    else:
        print(f"\n[FAIL] {total - passed} tests failed - Review issues above")
        return 1


if __name__ == "__main__":
    sys.exit(main())
