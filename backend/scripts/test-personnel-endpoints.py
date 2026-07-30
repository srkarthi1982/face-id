#!/usr/bin/env python
"""
Test Personnel Module Endpoints

This script tests all 8 Personnel API endpoints to verify they work correctly.

Prerequisites:
- Backend server running on http://localhost:8000
- Valid auth token with personnel:read and personnel:write permissions

Usage:
    cd backend
    uv run python scripts/test-personnel-endpoints.py
"""

import sys
import json
from pathlib import Path
import requests

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
TOKEN = ""  # Will be set below

# Test data
TEST_PERSONNEL_1 = {
    "emp_no": "EMP001",
    "full_name": "John Doe",
    "gender": 1,
    "email": "john.doe@example.com",
    "phone": "+1234567890",
    "date_of_birth": "1990-01-15",
    "nationality": "American",
    "idcard_num": "ID123456",
    "id_number": "NAT789012",
    "card_no": "CARD001",
    "department_id": None,
    "position": "Software Engineer",
    "hire_date": "2024-01-01",
    "push_to_device": False,
    "org_id": None,
    "person_id_internal": "test-person-001",
    "person_id_device": "device-001",
    "permissions": {},
    "pass_time": None,
    "is_active": True
}

TEST_PERSONNEL_2 = {
    "emp_no": "EMP002",
    "full_name": "Jane Smith",
    "gender": 2,
    "email": "jane.smith@example.com",
    "phone": "+0987654321",
}


def print_header(text: str):
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80)


def print_subheader(text: str):
    print(f"\n{text}")
    print("-" * 80)


def status_ok():
    return "[PASS]"


def status_fail():
    return "[FAIL]"


def get_auth_token():
    """Get auth token by logging in as admin."""
    print_subheader("Getting Auth Token...")
    
    # Try to get token - you may need to adjust this based on your auth setup
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        # Try the auth/login endpoint
        response = requests.post(f"{BASE_URL.replace('/api/v1', '')}/auth/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            # Check different response formats
            token = data.get("access_token") or data.get("data", {}).get("access_token")
            if token:
                print(f"  [OK] Got auth token: {token[:20]}...")
                return token
            else:
                print(f"  [WARN] Login succeeded but no token in response")
                print(f"       Response keys: {list(data.keys())}")
        else:
            print(f"  [WARN] Could not auto-login. Status: {response.status_code}")
            print("  Will try without token - some endpoints may return 401/403")
    except Exception as e:
        print(f"  [WARN] Login failed: {e}")
        print("  Will try without token - some endpoints may return 401/403")
    
    return None


def make_request(method: str, endpoint: str, json_data=None, params=None):
    """Make authenticated request."""
    headers = {}
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=json_data)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=json_data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            raise ValueError(f"Unknown method: {method}")
        
        return response
    except requests.exceptions.ConnectionError:
        print(f"  [FAIL] Could not connect to {url}")
        print("  Is the backend server running on http://localhost:8000?")
        sys.exit(1)


def test_create_personnel():
    """Test POST /personnel/ - Create personnel"""
    print_subheader("Test 1: POST /personnel/ (Create)")
    
    response = make_request("POST", "/personnel/", json_data=TEST_PERSONNEL_1)
    
    if response.status_code == 201:
        data = response.json()
        print(f"  [OK] Created personnel: ID={data.get('data', {}).get('id')}")
        print(f"       emp_no={data['data']['emp_no']}, name={data['data']['full_name']}")
        return data['data']
    else:
        print(f"  [FAIL] Status: {response.status_code}")
        print(f"       Response: {response.text[:200]}")
        return None


def test_create_duplicate_emp_no():
    """Test creating duplicate emp_no (should fail)"""
    print_subheader("Test 2: POST /personnel/ (Duplicate emp_no - Should Fail)")
    
    duplicate_data = TEST_PERSONNEL_1.copy()
    duplicate_data["full_name"] = "Duplicate Test"
    
    response = make_request("POST", "/personnel/", json_data=duplicate_data)
    
    if response.status_code == 400 or response.status_code == 409:
        print(f"  [OK] Correctly rejected duplicate emp_no")
        print(f"       Error: {response.json().get('detail', 'Unknown error')[:100]}")
        return True
    else:
        print(f"  [FAIL] Should have rejected duplicate. Status: {response.status_code}")
        return False


def test_list_personnel():
    """Test GET /personnel/ - List personnel"""
    print_subheader("Test 3: GET /personnel/ (List)")
    
    response = make_request("GET", "/personnel/", params={"page": 1, "page_size": 10})
    
    if response.status_code == 200:
        data = response.json()
        items = data.get("data", [])
        meta = data.get("meta", {})
        print(f"  [OK] Listed {len(items)} personnel")
        print(f"       Page: {meta.get('page')}/{meta.get('pages')}, Total: {meta.get('total')}")
        return True
    else:
        print(f"  [FAIL] Status: {response.status_code}")
        print(f"       Response: {response.text[:200]}")
        return False


def test_get_personnel(created_id: int):
    """Test GET /personnel/{id} - Get single personnel"""
    print_subheader(f"Test 4: GET /personnel/{created_id} (Get Single)")
    
    response = make_request("GET", f"/personnel/{created_id}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"  [OK] Retrieved personnel: {data['data']['full_name']}")
        return True
    else:
        print(f"  [FAIL] Status: {response.status_code}")
        return False


def test_update_personnel(created_id: int):
    """Test PUT /personnel/{id} - Update personnel"""
    print_subheader(f"Test 5: PUT /personnel/{created_id} (Update)")
    
    update_data = {
        "position": "Senior Software Engineer",
        "phone": "+1111111111"
    }
    
    response = make_request("PUT", f"/personnel/{created_id}", json_data=update_data)
    
    if response.status_code == 200:
        data = response.json()
        print(f"  [OK] Updated personnel")
        print(f"       New position: {data['data']['position']}")
        print(f"       New phone: {data['data']['phone']}")
        return True
    else:
        print(f"  [FAIL] Status: {response.status_code}")
        return False


def test_stats_endpoint():
    """Test GET /personnel/stats - Get statistics"""
    print_subheader("Test 6: GET /personnel/stats (Statistics)")
    
    response = make_request("GET", "/personnel/stats")
    
    if response.status_code == 200:
        data = response.json()
        stats = data.get("data", {})
        print(f"  [OK] Retrieved statistics:")
        print(f"       Total: {stats.get('total')}")
        print(f"       Active: {stats.get('active')}")
        print(f"       Inactive: {stats.get('inactive')}")
        print(f"       By Gender: {stats.get('by_gender')}")
        return True
    else:
        print(f"  [FAIL] Status: {response.status_code}")
        return False


def test_search_endpoint():
    """Test GET /personnel/search - Search personnel"""
    print_subheader("Test 7: GET /personnel/search (Search)")
    
    response = make_request("GET", "/personnel/search", params={"q": "John"})
    
    if response.status_code == 200:
        data = response.json()
        items = data.get("data", [])
        print(f"  [OK] Search returned {len(items)} results for 'John'")
        for item in items:
            print(f"       - {item['full_name']} ({item['emp_no']})")
        return True
    else:
        print(f"  [FAIL] Status: {response.status_code}")
        return False


def test_soft_delete(created_id: int):
    """Test DELETE /personnel/{id} - Soft delete"""
    print_subheader(f"Test 8: DELETE /personnel/{created_id} (Soft Delete)")
    
    response = make_request("DELETE", f"/personnel/{created_id}")
    
    if response.status_code == 204 or response.status_code == 200:
        print(f"  [OK] Personnel soft-deleted")
        return True
    else:
        print(f"  [FAIL] Status: {response.status_code}")
        return False


def test_restore(created_id: int):
    """Test POST /personnel/{id}/restore - Restore deleted personnel"""
    print_subheader(f"Test 9: POST /personnel/{created_id}/restore (Restore)")
    
    response = make_request("POST", f"/personnel/{created_id}/restore")
    
    if response.status_code == 200:
        data = response.json()
        print(f"  [OK] Personnel restored")
        print(f"       is_active: {data['data']['is_active']}")
        return True
    else:
        print(f"  [FAIL] Status: {response.status_code}")
        return False


def test_invalid_gender():
    """Test creating personnel with invalid gender"""
    print_subheader("Test 10: POST /personnel/ (Invalid gender - Should Fail)")
    
    invalid_data = TEST_PERSONNEL_2.copy()
    invalid_data["emp_no"] = "EMP_INVALID"
    invalid_data["gender"] = 5  # Invalid: must be 0, 1, or 2
    
    response = make_request("POST", "/personnel/", json_data=invalid_data)
    
    if response.status_code == 400 or response.status_code == 422:
        print(f"  [OK] Correctly rejected invalid gender")
        return True
    else:
        print(f"  [FAIL] Should have rejected invalid gender. Status: {response.status_code}")
        return False


def main():
    """Run all endpoint tests."""
    print_header("PERSONNEL MODULE - ENDPOINT TESTING")
    print(f"Base URL: {BASE_URL}")
    print(f"Server: http://localhost:8000")
    
    # Get auth token
    global TOKEN
    TOKEN = get_auth_token()
    
    if not TOKEN:
        print("\n[WARN] Running tests without authentication")
        print("Some endpoints may return 401/403 errors")
    
    results = []
    created_id = None
    
    # Test 1: Create personnel
    print_header("RUNNING TESTS")
    result = test_create_personnel()
    if result:
        created_id = result["id"]
        results.append(("Create Personnel", True))
    else:
        results.append(("Create Personnel", False))
        print("\n[ERROR] Cannot continue tests without created personnel")
        return 1
    
    # Test 2: Duplicate emp_no
    results.append(("Duplicate emp_no Rejection", test_create_duplicate_emp_no()))
    
    # Test 3: List personnel
    results.append(("List Personnel", test_list_personnel()))
    
    # Test 4: Get single personnel
    if created_id:
        results.append(("Get Single Personnel", test_get_personnel(created_id)))
    
    # Test 5: Update personnel
    if created_id:
        results.append(("Update Personnel", test_update_personnel(created_id)))
    
    # Test 6: Statistics
    results.append(("Statistics Endpoint", test_stats_endpoint()))
    
    # Test 7: Search
    results.append(("Search Endpoint", test_search_endpoint()))
    
    # Test 8: Soft delete
    if created_id:
        results.append(("Soft Delete", test_soft_delete(created_id)))
    
    # Test 9: Restore
    if created_id:
        results.append(("Restore Deleted", test_restore(created_id)))
    
    # Test 10: Invalid gender
    results.append(("Invalid Gender Rejection", test_invalid_gender()))
    
    # Summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = status_ok() if result else status_fail()
        print(f"{status} {test_name}")
    
    print("\n" + "=" * 80)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n[OK] ALL TESTS PASSED - Personnel module endpoints are working correctly!")
        return 0
    else:
        print(f"\n[FAIL] {total - passed} tests failed - Review issues above")
        return 1


if __name__ == "__main__":
    sys.exit(main())
