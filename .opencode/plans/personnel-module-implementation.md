# Personnel Module Implementation Plan

**Project:** JAC Face ID Management System  
**Module:** Personnel Management  
**Version:** Phase 1 (MVP)  
**Created:** 2026-07-23  
**Status:** Ready for Implementation  

---

## Overview

This plan details the Phase 1 implementation of the Personnel module, enabling CRUD operations for employee records with photo integration hooks and device sync flags.

**Goal:** Implement a complete personnel management system with independent PostgreSQL schema (no Luna DB migration).

**Timeline:** 2 weeks (10 working days)

**Team:** 2 Developers (1 Backend, 1 Frontend)

---

## Architecture Decisions

### Key Decisions

| Decision | Rationale |
|----------|-----------|
| **Independent Schema** | New PostgreSQL tables, no sync with Luna DB `employee` table |
| **Multi-tenancy** | Personnel scoped by `org_id` with unique `(emp_no, org_id)` constraint |
| **Modular Separation** | Departments, attendance, visitors handled by separate modules |
| **Soft Delete Only** | Use `is_active` flag; never hard delete personnel records |
| **Gender Codes** | 0=Unknown, 1=Male, 2=Female |

### Module Relationships

```
Personnel Module
├── Master Module (org_id → Organization)
├── Photos Module (person_id_internal → PhotoRegistration)
└── Person Mapping Module (device_person_mapping)
```

---

## Developer Assignments

### Developer 1: Backend Specialist
**Focus:** API, Database, Business Logic  
**Timeline:** Week 1-2

### Developer 2: Frontend Specialist
**Focus:** UI, State Management, User Experience  
**Timeline:** Week 1-2

---

## Backend Implementation (Developer 1)

### Track 1.1: Database Model
**File:** `backend/app/modules/personnel/models.py`  
**Time:** Day 1 (4-6 hours)

**Tasks:**
1. Define `Personnel` SQLAlchemy model with fields:
   - `id` (PK), `org_id` (FK → Organization)
   - `emp_no` (unique per org), `full_name`, `gender` (0/1/2)
   - `email`, `phone`, `date_of_birth`, `nationality`
   - `department_id` (FK → Location/Unit), `position`
   - `hire_date`, `is_active` (default=True)
   - Timestamps: `created_at`, `updated_at`

2. Add relationships:
   - `organization` (many-to-one)
   - `photo_registration` (one-to-one via `person_id_internal`)
   - `device_mappings` (one-to-many)

3. Create constraints:
   - Unique constraint: `uq_personnel_emp_no_org` on `(emp_no, org_id)`
   - Indexes: `idx_personnel_org_id`, `idx_personnel_emp_no`, `idx_personnel_is_active`

**Deliverable:** Complete model definition with all fields and relationships

---

### Track 1.2: Service Layer
**File:** `backend/app/modules/personnel/service.py`  
**Time:** Day 2 (6-8 hours)

**Tasks:**
1. Implement CRUD functions:
   - `create_personnel(db, org_id, emp_no, full_name, ...)` → `Personnel`
   - `get_personnel(db, personnel_id)` → `Personnel | None`
   - `update_personnel(db, personnel_id, updates)` → `Personnel`
   - `delete_personnel(db, personnel_id)` → Soft delete (set `is_active=False`)
   - `restore_personnel(db, personnel_id)` → Set `is_active=True`

2. Implement list/query functions:
   - `list_personnel(db, org_id, page, per_page, sort_by, order, filters)` → `(List[Personnel], total)`
   - Support filters: `is_active`, `gender`, `search` (name/email/emp_no)
   - Support sorting: `emp_no`, `full_name`, `hire_date`, `created_at`

3. Add validation:
   - Check `emp_no` uniqueness per `org_id` before create/update
   - Validate `gender` in (0, 1, 2)
   - Validate `org_id` exists

4. Add statistics function:
   - `get_personnel_stats(db, org_id)` → `{total, active, inactive, by_gender}`

**Deliverable:** Complete service layer with all CRUD + query + validation logic

---

### Track 1.3: Router & Endpoints
**File:** `backend/app/modules/personnel/router.py`  
**Time:** Day 3 (4-6 hours)

**Tasks:**
1. Define 8 API endpoints:

| Method | Path | Permission | Description |
|--------|------|------------|-------------|
| POST | `/api/v1/personnel` | `personnel:write` | Create personnel |
| GET | `/api/v1/personnel` | `personnel:read` | List personnel (paginated) |
| GET | `/api/v1/personnel/{id}` | `personnel:read` | Get personnel details |
| PUT | `/api/v1/personnel/{id}` | `personnel:write` | Update personnel |
| DELETE | `/api/v1/personnel/{id}` | `personnel:write` | Soft delete |
| POST | `/api/v1/personnel/{id}/restore` | `personnel:write` | Restore deleted |
| GET | `/api/v1/personnel/stats` | `personnel:read` | Get statistics |
| GET | `/api/v1/personnel/search` | `personnel:read` | Advanced search |

2. Add dependencies:
   - `get_db` (database session)
   - `get_current_user` (authentication)
   - `require_permission(PERSONNEL_READ/WRITE)` (authorization)

3. Add audit logging:
   - Log all create/update/delete operations
   - Include user_id, action, timestamp, changes

4. Error handling:
   - 404 for not found
   - 400 for validation errors
   - 403 for permission denied
   - 409 for duplicate `emp_no`

**Deliverable:** Complete router with all endpoints, permissions, and error handling

---

### Track 1.4: Alembic Migration
**File:** `backend/alembic/versions/{version}_add_personnel_module.py`  
**Time:** Day 4 (2-3 hours)

**Tasks:**
1. Generate migration:
   ```bash
   cd backend
   uv run alembic revision --autogenerate -m "add personnel module"
   ```

2. Verify migration includes:
   - `personnel` table creation with all columns
   - Foreign key constraints (`org_id`, `department_id`)
   - Unique constraint `uq_personnel_emp_no_org`
   - Indexes for performance

3. Test migration:
   ```bash
   uv run alembic upgrade head
   uv run alembic downgrade -1  # Test rollback
   uv run alembic upgrade head  # Re-apply
   ```

4. Verify in database:
   - Check table structure
   - Verify constraints and indexes
   - Test unique constraint (try duplicate `emp_no`)

**Deliverable:** Tested migration script that upgrades/rolls back cleanly

---

### Track 1.5: Backend Testing
**Time:** Day 5 (4-6 hours)

**Tasks:**
1. Test via Swagger UI (`http://localhost:8000/docs`):
   - Create personnel → Verify response
   - List personnel → Verify pagination
   - Update personnel → Verify changes
   - Soft delete → Verify `is_active=False`
   - Restore → Verify `is_active=True`

2. Test permissions:
   - Access without token → 401
   - Access with user lacking permission → 403
   - Access with admin → 200

3. Test edge cases:
   - Duplicate `emp_no` in same org → 409
   - Same `emp_no` in different org → 200 (allowed)
   - Invalid `gender` value → 400
   - Non-existent `org_id` → 400

4. Test audit logs:
   - Verify logs created for CRUD operations
   - Check log content accuracy

**Deliverable:** All endpoints tested and working; permissions enforced

---

## Frontend Implementation (Developer 2)

### Track 2.1: Zustand Store
**File:** `frontend/src/modules/personnel/store.ts`  
**Time:** Day 1-2 (4-6 hours)

**Tasks:**
1. Import dependencies:
   ```ts
   import '../../../api/client'  // ALWAYS first
   import { createCrudStore } from '../../../infra/shared/utils/createCrudStore'
   import {
       listPersonnelApiV1PersonnelEndpointGet as listPersonnel,
       createPersonnelApiV1PersonnelEndpointPost as createPersonnel,
       updatePersonnelApiV1PersonnelEndpointPut as updatePersonnel,
       deletePersonnelApiV1PersonnelEndpointDelete as deletePersonnel,
   } from '../../../api/generated'
   ```

2. Create store using factory:
   ```ts
   const usePersonnelStore = createCrudStore<PersonnelResponse>({
       listApi: listPersonnel,
       createApi: createPersonnel,
       updateApi: updatePersonnel,
       deleteApi: deletePersonnel,
       idPath: (id) => ({ personnel_id: id }),
   })
   ```

3. Export store:
   ```ts
   export default usePersonnelStore
   ```

**Deliverable:** Working Zustand store with CRUD operations

---

### Track 2.2: List Page
**File:** `frontend/src/modules/personnel/PersonnelListPage.tsx`  
**Time:** Day 3 (6-8 hours)

**Tasks:**
1. Import dependencies:
   ```tsx
   import { useShallow } from 'zustand/react/shallow'
   import { useI18n } from '../../../infra/locales/I18nContext'
   import CrudPage from '../../../infra/shared/components/CrudPage'
   import SectionHeader from '../../../infra/shared/components/SectionHeader'
   import usePersonnelStore from './store'
   import type { ValidTranslationKeys } from '../../../infra/locales/i18n'
   ```

2. Define columns:
   ```tsx
   const columns = [
       { key: 'emp_no', label: t('personnel.columns.emp_no'), sortable: true, filterable: true },
       { key: 'full_name', label: t('personnel.columns.full_name'), sortable: true, filterable: true },
       { key: 'gender', label: t('personnel.columns.gender'), sortable: true, render: renderGender },
       { key: 'department', label: t('personnel.columns.department'), filterable: true },
       { key: 'position', label: t('personnel.columns.position') },
       { key: 'status', label: t('personnel.columns.status'), render: renderStatus },
   ]
   ```

3. Define form fields:
   ```tsx
   const formFields = [
       { name: 'emp_no', label: t('personnel.form.emp_no'), required: true, type: 'text' },
       { name: 'full_name', label: t('personnel.form.full_name'), required: true, type: 'text' },
       { name: 'gender', label: t('personnel.form.gender'), type: 'select', options: genderOptions },
       { name: 'email', label: t('personnel.form.email'), type: 'email' },
       { name: 'phone', label: t('personnel.form.phone'), type: 'text' },
       { name: 'date_of_birth', label: t('personnel.form.dob'), type: 'date' },
       { name: 'department_id', label: t('personnel.form.department'), type: 'select' },
       { name: 'position', label: t('personnel.form.position'), type: 'text' },
       { name: 'hire_date', label: t('personnel.form.hire_date'), type: 'date' },
   ]
   ```

4. Implement page component:
   ```tsx
   export default function PersonnelListPage() {
       const { t } = useI18n()
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

       return (
           <div className="flex flex-col gap-6">
               <SectionHeader icon={<HiOutlineUsers />} title={t('nav.personnel')} />
               <CrudPage
                   title={t('personnel.title')}
                   items={items}
                   onFetch={fetch}
                   totalPages={pagination.pages}
                   onCreate={create}
                   onUpdate={update}
                   onDelete={remove}
                   columns={columns}
                   formFields={formFields}
               />
           </div>
       )
   }
   ```

5. Add helper functions:
   - `renderGender(gender: number)` → "Male" | "Female" | "Unknown"
   - `renderStatus(is_active: boolean)` → Badge component

**Deliverable:** Complete list page with CRUD functionality

---

### Track 2.3: Translations
**Files:** `frontend/src/infra/locales/en.json` & `ar.json`  
**Time:** Day 4 (2-3 hours)

**Tasks:**
1. Add English translations (`en.json`):
   ```json
   {
     "nav": {
       "personnel": "Personnel"
     },
     "personnel": {
       "title": "Personnel Management",
       "columns": {
         "emp_no": "Employee Number",
         "full_name": "Full Name",
         "gender": "Gender",
         "department": "Department",
         "position": "Position",
         "status": "Status"
       },
       "form": {
         "emp_no": "Employee Number",
         "full_name": "Full Name",
         "gender": "Gender",
         "email": "Email",
         "phone": "Phone",
         "dob": "Date of Birth",
         "department": "Department",
         "position": "Position",
         "hire_date": "Hire Date"
       },
       "gender": {
         "unknown": "Unknown",
         "male": "Male",
         "female": "Female"
       },
       "status": {
         "active": "Active",
         "inactive": "Inactive"
       },
       "actions": {
         "create": "Add Personnel",
         "edit": "Edit Personnel",
         "delete": "Deactivate Personnel",
         "restore": "Restore Personnel"
       },
       "messages": {
         "create_success": "Personnel created successfully",
         "update_success": "Personnel updated successfully",
         "delete_success": "Personnel deactivated successfully",
         "restore_success": "Personnel restored successfully",
         "duplicate_emp_no": "Employee number already exists in this organization"
       }
     }
   }
   ```

2. Add Arabic translations (`ar.json`):
   ```json
   {
     "nav": {
       "personnel": "الموظفين"
     },
     "personnel": {
       "title": "إدارة الموظفين",
       "columns": {
         "emp_no": "رقم الموظف",
         "full_name": "الاسم الكامل",
         "gender": "الجنس",
         "department": "القسم",
         "position": "المنصب",
         "status": "الحالة"
       },
       "form": {
         "emp_no": "رقم الموظف",
         "full_name": "الاسم الكامل",
         "gender": "الجنس",
         "email": "البريد الإلكتروني",
         "phone": "الهاتف",
         "dob": "تاريخ الميلاد",
         "department": "القسم",
         "position": "المنصب",
         "hire_date": "تاريخ التعيين"
       },
       "gender": {
         "unknown": "غير معروف",
         "male": "ذكر",
         "female": "أنثى"
       },
       "status": {
         "active": "نشط",
         "inactive": "غير نشط"
       },
       "actions": {
         "create": "إضافة موظف",
         "edit": "تعديل موظف",
         "delete": "إلغاء تفعيل موظف",
         "restore": "استعادة موظف"
       },
       "messages": {
         "create_success": "تم إضافة الموظف بنجاح",
         "update_success": "تم تحديث الموظف بنجاح",
         "delete_success": "تم إلغاء تفعيل الموظف بنجاح",
         "restore_success": "تم استعادة الموظف بنجاح",
         "duplicate_emp_no": "رقم الموظف موجود مسبقاً في هذه المؤسسة"
       }
     }
   }
   ```

3. Verify TypeScript compilation:
   ```bash
   npm run type-check
   ```

**Deliverable:** Complete translations in both languages; no TypeScript errors

---

### Track 2.4: Integration & Testing
**Time:** Day 5 (4-6 hours)

**Tasks:**
1. Run frontend dev server:
   ```bash
   cd frontend
   npm run dev
   ```

2. Test CRUD operations:
   - Navigate to Personnel page
   - Create new personnel → Verify in list
   - Edit personnel → Verify changes saved
   - Delete personnel → Verify status badge changes
   - Restore personnel → Verify status returns to active

3. Test pagination:
   - Create 20+ personnel records
   - Verify page navigation works
   - Verify sorting by columns

4. Test form validation:
   - Submit empty required fields → Verify errors
   - Submit invalid email → Verify error
   - Submit duplicate emp_no → Verify error message

5. Test translations:
   - Switch language to Arabic → Verify all text translated
   - Switch back to English → Verify all text translated

6. Test responsive design:
   - Resize browser window
   - Test on mobile viewport
   - Verify table scrolls horizontally if needed

7. Test theme compatibility:
   - Switch to dark mode → Verify colors
   - Switch to light mode → Verify colors

**Deliverable:** Fully functional Personnel page; all CRUD operations working

---

## Joint Tasks (Both Developers)

### Integration Testing
**Time:** End of Week 2 (2-3 hours together)

**Tasks:**
1. Verify API contract:
   - Backend response matches frontend expectations
   - Field names and types align
   - Error messages display correctly

2. Test end-to-end flow:
   ```
   Create → List → Update → Soft Delete → Restore
   ```

3. Test error scenarios:
   - Backend returns 409 (duplicate) → Frontend shows correct message
   - Backend returns 403 (permission) → Frontend shows unauthorized
   - Backend returns 404 (not found) → Frontend handles gracefully

4. Verify audit logs:
   - Create personnel → Check audit log entry
   - Update personnel → Check audit log shows changes
   - Delete personnel → Check audit log shows soft delete

**Deliverable:** End-to-end flow verified; no integration issues

---

## Week-by-Week Schedule

### Week 1

| Day | Backend Developer | Frontend Developer |
|-----|-------------------|-------------------|
| **Day 1** | Track 1.1: Model definition | Track 2.1: Zustand store |
| **Day 2** | Track 1.2: Service layer | Track 2.1: Continue store (if needed) |
| **Day 3** | Track 1.3: Router endpoints | Track 2.2: List page |
| **Day 4** | Track 1.4: Migration | Track 2.3: Translations |
| **Day 5** | Track 1.5: Backend testing | Track 2.2: Continue list page (if needed) |

### Week 2

| Day | Backend Developer | Frontend Developer |
|-----|-------------------|-------------------|
| **Day 6** | Fix bugs from testing | Track 2.4: Integration testing |
| **Day 7** | Support frontend integration | Track 2.4: Continue integration |
| **Day 8** | Joint: Integration testing | Joint: Integration testing |
| **Day 9** | Joint: Polish & edge cases | Joint: Polish & edge cases |
| **Day 10** | Phase 2 planning | Phase 2 planning |

---

## Definition of Done (Phase 1)

### Backend Criteria
- [ ] `Personnel` model defined with all fields and relationships
- [ ] Service layer implements all CRUD + query functions
- [ ] Router exposes 8 endpoints with correct permissions
- [ ] Migration script tested (upgrade/rollback)
- [ ] All endpoints tested via Swagger UI
- [ ] Permissions enforced correctly
- [ ] Audit logging working
- [ ] Error handling complete (400, 401, 403, 404, 409)

### Frontend Criteria
- [ ] Zustand store implements CRUD operations
- [ ] List page displays personnel with pagination
- [ ] Form modal supports create/edit
- [ ] Soft delete changes status badge
- [ ] Translations complete in English and Arabic
- [ ] Form validation working
- [ ] Responsive design tested
- [ ] Dark/light theme compatible
- [ ] TypeScript compilation passes

### Integration Criteria
- [ ] End-to-end CRUD flow verified
- [ ] Error messages display correctly
- [ ] Audit logs created for all operations
- [ ] No console errors in browser
- [ ] Performance acceptable (<500ms API responses)

---

## Phase 2 Preview (Post-MVP)

**Timeline:** Week 3-4 (after Phase 1 completion)

### Planned Features

| Feature | Description | Priority |
|---------|-------------|----------|
| **Bulk Import** | CSV/Excel upload for批量 personnel creation | High |
| **Bulk Export** | Download personnel list as CSV/Excel | High |
| **Advanced Search** | Multi-field search with filters | High |
| **Photo Integration** | Link personnel to photo registration | High |
| **Device Sync** | Push personnel to face ID devices | Medium |
| **Department Filter** | Filter by department/location | Medium |
| **Statistics Dashboard** | Charts and metrics | Low |

### Phase 2 Planning Tasks
1. Review Phase 1 lessons learned
2. Detail bulk import/export specifications
3. Design advanced search UI
4. Plan photo integration workflow
5. Coordinate with device sync module

---

## Key Files Reference

### Backend Files
| File | Purpose |
|------|---------|
| `backend/app/modules/personnel/models.py` | SQLAlchemy model |
| `backend/app/modules/personnel/schemas.py` | Pydantic schemas |
| `backend/app/modules/personnel/service.py` | Business logic |
| `backend/app/modules/personnel/router.py` | API endpoints |
| `backend/app/core/permissions.py` | Permission codes |
| `backend/alembic/versions/*.py` | Database migration |

### Frontend Files
| File | Purpose |
|------|---------|
| `frontend/src/modules/personnel/store.ts` | Zustand store |
| `frontend/src/modules/personnel/PersonnelListPage.tsx` | Main list page |
| `frontend/src/infra/locales/en.json` | English translations |
| `frontend/src/infra/locales/ar.json` | Arabic translations |
| `frontend/src/infra/shared/components/CrudPage.tsx` | Generic CRUD component |
| `frontend/src/infra/shared/utils/createCrudStore.ts` | Store factory |

### Related Modules
| Module | Relationship |
|--------|--------------|
| `backend/app/modules/master/` | Organization (FK) |
| `backend/app/modules/photos/` | Photo registration (1:1) |
| `backend/app/modules/person_mapping/` | Device mapping (1:N) |

---

## Testing Checklist

### Backend Testing
```bash
# Start backend
cd backend
uv run uvicorn app.main:app --reload --port 8000

# Test endpoints via Swagger UI
# http://localhost:8000/docs

# Test migration
uv run alembic upgrade head
uv run alembic downgrade -1
uv run alembic upgrade head
```

### Frontend Testing
```bash
# Start frontend
cd frontend
npm run dev

# Type check
npm run type-check

# Build (pre-push)
npm run build
```

### Integration Testing
```bash
# Test both together
# Backend: http://localhost:8000
# Frontend: http://localhost:5175

# Verify CRUD operations
# Verify error handling
# Verify translations
```

---

## Support & Questions

**For Backend Questions:**
- Review existing modules (e.g., `device`, `users`) for patterns
- Check `backend/app/core/database.py` for SQLAlchemy setup
- Refer to `backend/app/core/permissions.py` for permission codes

**For Frontend Questions:**
- Review existing modules (e.g., `device-management`) for patterns
- Check `CrudPage.tsx` for component API
- Refer to `createCrudStore.ts` for store factory usage

**For Integration Questions:**
- Test via Swagger UI first
- Verify API contract (request/response shapes)
- Check network tab for errors

---

## Success Metrics

| Metric | Target |
|--------|--------|
| API Response Time | <500ms (p95) |
| Frontend Load Time | <2s |
| TypeScript Errors | 0 |
| Test Coverage | >80% (future goal) |
| User Satisfaction | Positive feedback |

---

**Document Version:** 1.0  
**Last Updated:** 2026-07-23  
**Maintained By:** Development Team  
**Access:** Internal Use Only
