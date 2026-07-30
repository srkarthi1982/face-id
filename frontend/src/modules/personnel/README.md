# Personnel Module

## Purpose

Personnel management — manage employee records with comprehensive HR data, CRUD operations, status control, and device synchronization support.

## Key Files

### Core Files
- `PersonnelPage.tsx` — Module entry point
- `PersonnelListPage.tsx` — Main list page with CRUD functionality
- `PhotoUploadModal.tsx` — Per-person photo upload modal (row "Photo" action); shows the current master photo and uploads JPEG/PNG (max 5 MB) via `POST /api/v1/photo/upload` (multipart)
- `PushToDeviceModal.tsx` — Per-person device sync modal (row "Push" action); pick target devices (+ optional registration photo) and call `POST /api/v1/personnel/{id}/push`, showing per-device success/failure results
- `store.ts` — Zustand store for personnel state management
- `manifest.ts` — Module manifest with routing and permissions
- `README.md` — This documentation

### Infrastructure
- `../../api/generated/index.ts` — TypeScript type definitions
- `../../infra/locales/en.json` — English translations
- `../../infra/locales/ar.json` — Arabic translations

## Store

**Store:** `usePersonnelStore` (manual Zustand pattern)

**State:**
- `items: PersonnelItem[]` — List of personnel records
- `pagination` — Pagination metadata (page, page_size, total, pages)
- `isLoading: boolean` — Loading state

**Operations:**
- `fetch(page, params)` — Fetch personnel with pagination, sorting, and filtering
- `create(payload)` — Create new personnel record
- `update(id, payload)` — Update existing personnel record
- `remove(id)` — Delete personnel record (soft delete)
- `restore(id)` — Restore soft-deleted personnel
- `reset()` — Reset store to initial state

**Usage Example:**
```tsx
import { useShallow } from 'zustand/react/shallow'
import { usePersonnelStore } from './store'

const { items, pagination, fetch, create, update, remove } = usePersonnelStore(
    useShallow((s) => ({
        items: s.items,
        pagination: s.pagination,
        fetch: s.fetch,
        create: s.create,
        update: s.update,
        remove: s.remove,
    }))
)
```

## Pages

| Page | Path | Description | Permissions |
|------|------|-------------|-------------|
| PersonnelPage | `/personnel` | Module entry (renders PersonnelListPage) | personnel:read |
| PersonnelListPage | `/personnel` | Personnel list with CRUD operations | personnel:read |

## API Integration

### Endpoints Used
- `GET /api/v1/personnel/` — List personnel with pagination, sorting, filtering
- `POST /api/v1/personnel/` — Create personnel
- `GET /api/v1/personnel/{id}` — Get single personnel
- `PUT /api/v1/personnel/{id}` — Update personnel
- `DELETE /api/v1/personnel/{id}` — Delete personnel (soft delete)
- `POST /api/v1/personnel/{id}/restore` — Restore deleted personnel
- `GET /api/v1/personnel/stats` — Get personnel statistics
- `GET /api/v1/personnel/search` — Search personnel

### Request/Response Format

**List Request:**
```
GET /api/v1/personnel/?page=1&page_size=20&org_id=1&sort_by=emp_no&order=asc
    &filters.emp_no=EMP001&filters.full_name=John&filters.is_active=true
```

**List Response:**
```json
{
  "success": true,
  "data": [PersonnelItem, ...],
  "meta": {
    "page": 1,
    "page_size": 20,
    "total": 100,
    "pages": 5
  }
}
```

**Create Payload:**
```json
{
  "emp_no": "EMP001",
  "full_name": "John Doe",
  "gender": 1,
  "email": "john@example.com",
  "phone": "+1234567890",
  "date_of_birth": "1990-01-01",
  "nationality": "Nationality",
  "idcard_num": "ID123456",
  "id_number": "NID123456",
  "card_no": "CARD123",
  "department_id": 5,
  "position": "Manager",
  "hire_date": "2020-01-01",
  "org_id": 1,
  "push_to_device": false,
  "is_active": true
}
```

## Personnel Data Model

**PersonnelItem Fields:**

### Identification
- `id: number` — Unique identifier
- `org_id?: number | null` — Organization ID (FK to locations)
- `emp_no: string` — Employee number (unique per organization)
- `person_id_internal?: string | null` — Internal person ID
- `person_id_device?: string | null` — Device-specific ID

### Personal Information
- `full_name: string` — Full name
- `gender: number` — Gender (0=Unknown, 1=Male, 2=Female)
- `date_of_birth?: string | null` — Date of birth (YYYY-MM-DD)
- `nationality?: string | null` — Nationality

### Contact Information
- `email?: string | null` — Email address
- `phone?: string | null` — Phone number

### Identification Numbers
- `idcard_num?: string | null` — ID card number
- `id_number?: string | null` — National ID number
- `card_no?: string | null` — Card number

### Employment Information
- `department_id?: number | null` — Department ID (FK to locations)
- `position?: string | null` — Job position
- `hire_date?: string | null` — Hire date (YYYY-MM-DD)

### Device Sync & Access
- `permissions: Record<string, unknown>` — Access permissions
- `pass_time?: Record<string, unknown> | null` — Pass time configuration
- `push_to_device: boolean` — Sync to device flag

### Status & Timestamps
- `is_active: boolean` — Active status
- `created_at: string` — Creation timestamp
- `updated_at: string` — Last update timestamp

## End-to-End Flow

### View Personnel List
```
1. User navigates to /personnel
2. PersonnelPage renders PersonnelListPage
3. PersonnelListPage fetches data via usePersonnelStore.fetch(1)
4. API call: GET /api/v1/personnel/?page=1&page_size=20
5. Store updates items and pagination state
6. CrudPage renders table with 8 columns
```

### Create Personnel
```
1. User clicks "Add New" button
2. Modal opens with 14 form fields
3. User fills required fields (emp_no, full_name, gender)
4. User clicks "Create"
5. CrudPage calls store.create(payload)
6. API call: POST /api/v1/personnel/
7. Backend validates emp_no uniqueness within org
8. Store re-fetches current page
9. Modal closes, table updates
```

### Update Personnel
```
1. User clicks edit icon on a row
2. Modal opens with pre-filled form
3. User modifies fields
4. User clicks "Update"
5. CrudPage calls store.update(id, payload)
6. API call: PUT /api/v1/personnel/{id}
7. Backend validates emp_no uniqueness if changed
8. Store re-fetches current page
9. Modal closes, table updates
```

### Delete Personnel (Soft Delete)
```
1. User clicks delete icon on a row
2. Confirmation dialog appears
3. User confirms deletion
4. CrudPage calls store.remove(id)
5. API call: DELETE /api/v1/personnel/{id}
6. Backend sets is_active = false
7. Store re-fetches current page
8. Table updates, row removed from active view
```

### Restore Personnel
```
1. Filter shows inactive personnel
2. User clicks restore action
3. API call: POST /api/v1/personnel/{id}/restore
4. Backend sets is_active = true
5. Store re-fetches current page
6. Personnel restored to active list
```

## Permissions

**Module Access:** `personnel:read`

**Operations:**
- List/View: `personnel:read`
- Create: `personnel:write`
- Update: `personnel:write`
- Delete: `personnel:write`
- Restore: `personnel:write`

Permission is checked at:
1. Module level (manifest.ts) — controls sidebar visibility and route access
2. API level (backend) — enforces permission on each endpoint

## Translations

**Namespace:** `personnel.fields.*` and `personnel.gender.*`

**Available Keys:**

### Fields (22 keys)
- `personnel.fields.id` — ID
- `personnel.fields.org_id` — Organization
- `personnel.fields.emp_no` — Employee Number
- `personnel.fields.person_id_internal` — Internal ID
- `personnel.fields.person_id_device` — Device ID
- `personnel.fields.full_name` — Full Name
- `personnel.fields.gender` — Gender
- `personnel.fields.email` — Email
- `personnel.fields.phone` — Phone
- `personnel.fields.date_of_birth` — Date of Birth
- `personnel.fields.nationality` — Nationality
- `personnel.fields.idcard_num` — ID Card Number
- `personnel.fields.id_number` — ID Number
- `personnel.fields.card_no` — Card Number
- `personnel.fields.department_id` — Department
- `personnel.fields.position` — Position
- `personnel.fields.hire_date` — Hire Date
- `personnel.fields.permissions` — Permissions
- `personnel.fields.pass_time` — Pass Time
- `personnel.fields.push_to_device` — Push to Device
- `personnel.fields.is_active` — Status
- `personnel.fields.created_at` — Created At
- `personnel.fields.updated_at` — Updated At

### Gender Values (3 keys)
- `personnel.gender.unknown` — Unknown
- `personnel.gender.male` — Male
- `personnel.gender.female` — Female

**Common Keys Used:**
- `common.id` — ID
- `common.active` — Active
- `common.inactive` — Inactive
- `common.yes` — Yes
- `common.no` — No

Languages: English (en), Arabic (ar)

## Component Structure

```
PersonnelPage (module entry)
  └─ PersonnelListPage
      ├─ SectionHeader (page header with icon)
      └─ CrudPage (generic CRUD UI component)
          ├─ SearchBar (filter by name, emp_no, etc.)
          ├─ Table (personnel list)
          │   ├─ 8 sortable columns
          │   └─ Filterable columns (emp_no, full_name)
          ├─ Paginator (pagination controls)
          └─ Modal (create/edit form)
              └─ 14 form fields
```

## Related Modules

- `device` — Face ID devices that recognize personnel
- `photos` — Face photo registrations for personnel
- `person_mapping` — Device-person mapping configurations
- `master` — Location and unit master data (for organization/department)
- `recognition_records` — Access logs for personnel

## Business Rules

### Validation
1. **Employee Number Uniqueness:** `emp_no` must be unique within an organization
2. **Gender Codes:** Must be 0 (Unknown), 1 (Male), or 2 (Female)
3. **Organization Exists:** `org_id` must reference a valid location
4. **Department Exists:** `department_id` must reference a valid location (if provided)
5. **Date Formats:** Dates should be in YYYY-MM-DD format

### Soft Delete
- Delete operation sets `is_active = false` instead of removing record
- Deleted personnel can be restored via restore endpoint
- Inactive personnel hidden from default list views

### Multi-Tenancy
- Personnel belong to an organization (`org_id`)
- Organization filtering enables multi-tenancy
- Employee numbers unique per organization, not globally

## Future Enhancements (Phase 2+)

- [ ] Bulk import/export (CSV, Excel)
- [ ] Advanced search with saved filters
- [ ] Photo upload integration
- [ ] Device sync status display
- [ ] Personnel statistics dashboard
- [ ] Export personnel list to PDF
- [ ] Audit log viewer for personnel changes
- [ ] Batch status updates
- [ ] Duplicate detection
- [ ] Organization/department dropdown with hierarchy
- [ ] Date pickers for DOB and hire_date
- [ ] Email/phone validation

## Testing Checklist

- [x] Store creation with CRUD operations
- [x] List page with CrudPage integration
- [x] Column definitions (8 columns)
- [x] Form field definitions (14 fields)
- [x] Translations (EN/AR)
- [x] Permission gating
- [x] Type definitions match backend
- [ ] End-to-end CRUD testing with backend
- [ ] Error handling verification
- [ ] Responsive design testing
- [ ] Theme compatibility (light/dark modes)
- [ ] Pagination testing
- [ ] Filter functionality testing
- [ ] Sorting functionality testing
- [ ] Restore functionality testing

## Implementation Status

**Phase:** 1 (MVP) — COMPLETE ✅

**Tracks Completed:**
- ✅ Track 2.1: Store implementation (updated for backend)
- ✅ Track 2.2: List page implementation (updated for backend)
- ✅ Track 2.3: Translations (EN/AR complete)
- ⏳ Track 2.4: Integration testing (ready for testing)

**Files Created:** 4
**Files Modified:** 6
**Lines of Code:** ~600

## Backend Integration Notes

**Backend Model Differences:**
- Backend has 18+ fields vs. initial 7 fields
- Uses `emp_no` and `full_name` as primary identifiers
- Includes gender (0/1/2), contact info, employment details
- Uses `restore` endpoint instead of `activate/deactivate`
- Supports organization-based multi-tenancy
- Validates employee number uniqueness per organization

**API Alignment:**
- ✅ Store endpoints match backend router
- ✅ Type definitions match backend schemas
- ✅ Filtering supports backend filter params
- ✅ Sorting uses backend sort_by/order params
- ✅ Soft delete handled correctly (204 response)
