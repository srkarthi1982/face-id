# JAC Face Id Management System

## 1. Project Overview

JAC Face ID Management System — authentication, access control, and face recognition device management platform.

**Core Features:**
- User authentication (JWT, LDAP, OAuth2)
- Role-based access control (RBAC)
- Face ID device management (100+ devices)
- Personnel management with photo registration
- Recognition records and access logs
- Real-time device callbacks and event handling

**Infrastructure:**
- Backend: FastAPI + PostgreSQL (Windows Server 2022)
- Frontend: React 19 + Vite + Tailwind CSS

## 2. Technology Stack

**Backend:** FastAPI, SQLAlchemy, Alembic, PostgreSQL, python-jose, bcrypt, ldap3, slowapi

**Frontend:** React 19, TypeScript, Vite, Tailwind CSS, Zustand, React Router, dnd-kit, Playwright

**DevOps:** NSSM (Windows service), pg_dump, pg_basebackup

## 3. Project Structure

```
├── backend/              # FastAPI application
├── frontend/             # React application
├── scripts/              # Deployment, backup, setup scripts
├── docs/                 # API documentation
└── .opencode/plans/      # Feature implementation plans
```

## 4. Module Architecture (Backend)

| Module | Route Prefix | Purpose |
|--------|-------------|---------|
| auth | /api/v1/auth | Login, logout, register, refresh |
| users | /api/v1/users | User CRUD |
| access | /api/v1/access | Roles & permissions |
| profile | /api/v1/profile-info | User profiles |
| pat | /api/v1/pats | Personal access tokens |
| device | /api/v1/device | Face ID device management |
| personnel | /api/v1/personnel | Personnel records |
| photos | /api/v1/photo | Photo registrations |
| person_mapping | /api/v1/person-mapping | Device-person mapping |
| recognition_records | /api/v1/record | Access logs |
| callbacks | /api/v1/callback | Callback configurations |
| audit | /api/v1/audit-logs | Audit logging |
| shared | /api/v1/shared | Country reference data |
| master | /api/v1/master-data | Location and unit master data management |

**Module Pattern:** Each module has `models.py`, `schemas.py`, `router.py`, and optionally `service.py`

## 5. Module Architecture (Frontend)

**Auto-discovery:** Routes are auto-generated from `manifest.ts` files. No central registration file needed.

### Module Tree (by order)

  ```
  src/modules/
  ├── dashboard/                     path: /dashboard, order: 0
  ├── profile-general-info/          path: /profile-general-info, order: 1, permissions: ['hide:*']
  ├── personnel/                     path: /personnel, order: 10
  ├── master/                        path: /master, order: 12
  │   ├── location/                  path: locations, order: 10
  │   └── unit/                      path: units, order: 20
  ├── device/                        path: /device, order: 15
  │   └── device-management/         path: device-management, order: 10
  └── settings/                     path: /settings, order: 90, pinBottom
      ├── account/                  path: account, order: 5
      ├── access-management/       path: access-management/*, order: 10, permissions: ['admin:*']
      ├── users-management/         path: users, order: 20, permissions: ['admin:full']
      ├── appearance/               path: appearance, order: 25
    ├── language/                 path: language, order: 30
    └── audit-log/               path: audit-log, order: 30
```

### Manifest Reference

**ModuleManifest** (in `manifest.ts` at module root):
```ts
interface ModuleManifest {
  i18n: ValidTranslationKeys        // sidebar label
  icon: IconType                    // sidebar icon (react-icons)
  path: string                      // ABSOLUTE path e.g. '/settings'
  permissions?: PermissionPattern[] // access gate (any-of)
  pinBottom?: true                  // pin to sidebar bottom
  order?: number                    // lower = earlier (use gaps of 10)
  page?: ComponentType              // optional default page
}
```

**FeatureManifest** (in `manifest.ts` inside feature folder):
```ts
interface FeatureManifest {
  i18n: ValidTranslationKeys        // submenu label
  path: string                      // RELATIVE path e.g. 'account'
  page: ComponentType               // required
  permissions?: PermissionPattern[] // inherits from module if absent
  order?: number
}
```

**PermissionPattern:**
- Exact: `'user:read'`
- Prefix wildcard: `'chat:*'` matches `chat:read`, `chat:write`, etc.
- Global: `'*'` (public-with-auth)

### Top-Level src/ Layout

```
src/
├── api/                # auto-generated hey-api client + client.ts
├── infra/              # cross-cutting infrastructure
│   ├── auth/           # LoginPage, RegisterPage, useAuthStore
│   ├── config/         # menu.config.tsx (auto-discovery)
│   ├── locales/        # I18nContext + en.json + ar.json
│   ├── shared/
│   │   ├── components/ # CrudPage, Layout, SectionHeader, etc.
│   │   ├── pages/      # PlaceholderPage, NotFoundPage, UnauthorizedPage
│   │   ├── store/      # useToastStore, useLoadingStore, etc.
│   │   └── utils/      # createCrudStore, apiError, menuUtils
│   └── theme/          # ThemeContext
├── modules/            # feature modules (see tree above)
├── App.tsx
├── main.tsx
└── index.css
```

### Import Conventions

| Target | Import |
|--------|--------|
| Own store | `from './store'` |
| Module-level page (sibling) | `from '../<ModuleName>DefaultPage'` |
| Sibling feature | `from '../<other-feature>/...'` |
| Cross-module | `from '../../../<other-module>/<...>'` |
| Infra shared | `from '../../../infra/shared/...'` |
| i18n | `from '../../../infra/locales/I18nContext'` |
| Auth store | `from '../../../infra/auth/useAuthStore'` |
| Theme | `from '../../../infra/theme/ThemeContext'` |
| Generated API | `from '../../../api/generated'` |
| API client | `from '../../../api/client'` (**always first**) |

### Hidden Routes (no sidebar)

Routes wired statically in `App.tsx`:
- `/` → UserProfileInfoPage
- `/design-system` → DesignSystemPage (admin)
- `/login`, `/register`, `/unauthorized`

### Wildcard Paths (nested sub-routes)

Features needing nested pages declare wildcard path:
```ts
path: 'access-management/*',
page: AccessManagementRoutes,
```
Auto-discovery only globs 2 levels deep (`modules/*/manifest.ts` and `modules/*/*/manifest.ts`).

## 6. Key Infrastructure Files

**Backend:**
- `app/main.py` — FastAPI app, middleware, exception handlers
- `app/core/config.py` — Settings (Pydantic)
- `app/core/deps.py` — Dependency injection (get_db, get_current_user)
- `app/core/security.py` — JWT, bcrypt utilities
- `app/core/permissions.py` — Permission codes
- `app/core/database.py` — SQLAlchemy engine, Base, mixins
- `app/core/audit.py` — SQLAlchemy event listeners for audit
- `app/modules/__init__.py` — Router aggregation

**Frontend:**
- `src/api/client.ts` — Configured API client with interceptors
- `src/infra/config/menu.config.tsx` — Auto-discovers modules
- `src/infra/shared/utils/createCrudStore.ts` — CRUD store factory
- `src/infra/shared/components/CrudPage.tsx` — Generic CRUD component

## 7. Commands

### Backend
```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload --port 8000
uv run alembic revision --autogenerate -m "message"
uv run alembic upgrade head
```

### Frontend
```bash
cd frontend
npm install
npm run dev              # http://localhost:5175
npm run build            # TypeScript check + Vite build
npm run generate-types   # Generate API client + permissions (backend must be running)
npm run test:e2e         # Playwright tests
```

### ⚠️ Important: Server Management

**NEVER start or stop backend/frontend servers automatically.** Always ask the user to manually start/stop servers.

| Do NOT | Do Instead |
|--------|------------|
| `uv run uvicorn ...` | "Please start the backend server with: `uv run uvicorn app.main:app --reload --port 8000`" |
| `npm run dev` | "Please start the frontend dev server with: `npm run dev`" |
| Kill processes | "Please stop the backend/frontend server" |

**Rationale:** User maintains control over server state, port conflicts, and development environment.

## 8. Git Hooks (Husky)

| Hook | Command | Time | Catches |
|------|---------|------|---------|
| pre-commit | `npm run type-check` | ~5s | Type errors, missing imports |
| pre-push | `npm run build` | ~30-60s | Everything above + Vite errors |

```bash
# Fresh clone
cd frontend && npm install && npm run generate-types
```

## 9. Permissions Matrix

| Code | Scope |
|------|-------|
| user:read | View user list, details |
| user:write | Create/update/delete users |
| role:manage | Role & permission management |
| admin:full | Full admin access |
| admin:* | All admin permissions |
| device:read | View device list, status, settings, records |
| device:write | Add/remove/update devices, sync, manage settings |
| personnel:read | View personnel list and details |
| personnel:write | Add/update/delete personnel and sync to devices |
| record:read | View recognition records |
| record:write | Delete recognition records |
| audit:read | View audit logs |
| hide:* | Hidden from normal access |

**Re-run `npm run generate-permissions`** whenever backend `permissions.py` changes.

## 10. API Client Conventions

Generated functions follow naming:
```
{verb}{Resource}ApiV1{Prefix}{ResourcePath}{HttpMethod}
Example: listDevicesApiV1DeviceEndpointGet
```

**hey-api never throws.** Always returns `{ data, error }`:
```ts
// GOOD
const { data, error } = await createDeviceApi({ body: payload })
throwIfError(error)

// BAD — silently swallows errors
const result = await createDeviceApi({ body: payload })
```

Use short aliases:
```ts
import {
    listDevicesApiV1DeviceEndpointGet               as listDevices,
    createDeviceApiV1DeviceEndpointPost             as createDevice,
} from '../../../api/generated'
```

## 11. Store Patterns

### createCrudStore Factory (recommended for simple CRUD)

```ts
import '../../../api/client'  // ← ALWAYS first
import { createCrudStore } from '../../../infra/shared/utils/createCrudStore'

const useDeviceStore = createCrudStore<DeviceResponse>({
    listApi:   listDevices,
    createApi: createDevice,
    updateApi: updateDevice,
    deleteApi: deleteDevice,
    idPath:    (id) => ({ device_id: id }),
})
```

### useShallow is Required

**#1 cause of runtime errors** — infinite render loops without it:
```tsx
import { useShallow } from 'zustand/react/shallow'

const { items, fetch, create } = useDeviceStore(
    useShallow((s) => ({ items: s.items, fetch: s.fetch, create: s.create }))
)

// NEVER — causes infinite loop
const items = useDeviceStore((s) => s.items)
```

### Manual Store Pattern

For complex logic, use Zustand directly with standard state keys:
- `items`, `pagination`, `fetchParams`, `fetch`, `create`, `update`, `remove`
- After mutation: `get().fetch(get().pagination.page)`
- Always call `throwIfError(error)` before re-fetching

## 12. Page Creation

### Always Use useShallow + i18n

```tsx
import { useShallow } from 'zustand/react/shallow'
import { useI18n } from '../../../infra/locales/I18nContext'
const tk = (k: string) => k as ValidTranslationKeys
```

### Page Layout Rules

**The Layout owns page margins.** Pages must NOT add root padding:
```tsx
// BAD
<div className="px-9 pt-9 pb-10 max-w-3xl"> … </div>

// GOOD — bare root
<div className="flex flex-col gap-6"> … </div>
```

**Page header — use SectionHeader:**
```tsx
import SectionHeader from '../../../infra/shared/components/SectionHeader'
<SectionHeader icon={<HiOutlineCog />} title={t('nav.settings')} />
```

### CrudPage (standard CRUD)

```tsx
<CrudPage
    title={t('nav.device.devices.title')}
    items={items}
    onFetch={fetch}
    totalPages={pagination.pages}
    onCreate={create}
    onUpdate={update}
    onDelete={remove}
    columns={[
        { key: 'id',   label: t('common.id'),   sortable: true },
        { key: 'name', label: t('common.name'), sortable: true, filterable: true },
    ]}
    formFields={[
        { name: 'device_name', label: t('common.name'), required: true },
        { name: 'ip_address',  label: t('common.ip'),   type: 'text' },
    ]}
/>
```

**Column props:** `key`, `label`, `sortable?`, `filterable?`, `render?`

**FormField props:** `name`, `label`, `type?` (`'text'|'number'|'date'|'select'|'email'|'password'`), `required?`, `default?`, `options?`

### Full-Bleed Pages

For immersive views (readers, canvases):
```tsx
import useFullBleedStore from '../../../infra/shared/store/useFullBleedStore'

const setFullBleed = useFullBleedStore((s) => s.setFullBleed)
useEffect(() => {
    setFullBleed(true)
    return () => setFullBleed(false)
}, [setFullBleed])
// Root must be: className="flex flex-col h-full w-full"
```

## 13. i18n

**Always update BOTH `en.json` and `ar.json` simultaneously.**

```json
// en.json
{ "nav": { "device": { "devices": { "title": "Devices" } } } }

// ar.json
{ "nav": { "device": { "devices": { "title": "الأجهزة" } } } }
```

`ValidTranslationKeys` derived from `en.json` — TypeScript errors if key missing.

## 14. Theme & CSS Variables

**Always use CSS variables — never hardcode colors.**

| Token | Light | Dark | Use |
|-------|-------|------|-----|
| `bg-bg` | `#ECF0F6` | `#0B1221` | Page background |
| `bg-surface` | `#FFFFFF` | `#131D2E` | Cards, modals |
| `text-primary` | `#0D1B2A` | `#EEF2F8` | Body text |
| `text-accent` | `#06555C` | `#2DD4BF` | Accent text |
| `bg-accent` | `#06555C` | `#2DD4BF` | Primary buttons |
| `border-bd` | — | — | All borders |

**Special inline variables:** `var(--navy)` (thead), `var(--accent)`, `var(--success)`, `var(--danger)`, `var(--warning)`

## 15. Feature Plans

- `.opencode/plans/face-id-integration.md` — Face ID device integration architecture
- `.opencode/plans/face-id-phase-1.md` — Phase 1 implementation details

## 16. Database

- PostgreSQL with SQLAlchemy 2.0
- Alembic for migrations
- 14 tables: users, roles, permissions, profiles, devices, personnel, photos, recognition_records, callback_configs, device_person_mapping, device_task_logs, personal_access_tokens, countries, audit_logs

## 17. Face ID Device Integration (Planned)

**Architecture:**
- Backend pushes personnel/photos to devices (not pull)
- Devices push recognition records via callbacks (not polled)
- LAN discovery via subnet scanning

**New Backend Modules (Phase 2):**
- `app/devices/client.py` — HTTP client for 109 device API endpoints
- `app/devices/services.py` — Sync & task orchestration
- `app/devices/router.py` — Callback receivers
- `app/devices/handlers.py` — Callback payload processors

## 18. Known Gaps

- Phase 2: DeviceHttpClient, callback handlers, LAN discovery
- Phase 3: Frontend device pages, records viewer, dashboard
- Phase 4: S3 migration; generic background-worker framework (personnel bulk push implements an in-memory job pattern: `app/modules/personnel/push_jobs.py` + `POST /personnel/push-bulk`, `GET /personnel/push-jobs/{id}`, SSE `GET /personnel/push-jobs/{id}/events`, `POST /personnel/push-jobs/{id}/cancel` — single-process only, incompatible with `uvicorn --workers`)
- No unit/integration tests
- No CI/CD pipeline

## 19. Environment Variables

**Backend (`backend/.env`):**
| Variable | Description |
|----------|-------------|
| DATABASE_URL | PostgreSQL connection string |
| SECRET_KEY | JWT signing key (min 32 chars) |
| ACCESS_TOKEN_EXPIRE_MINUTES | JWT expiry (default: 30) |
| REFRESH_TOKEN_EXPIRE_DAYS | Refresh token expiry (default: 7) |
| LDAP_ENABLED | Enable LDAP authentication |
| ESNAAD_BASE_URL | ESNAAD external service URL |
| LOG_LEVEL | Logging level |

**Frontend (`frontend/.env`):**
| Variable | Description |
|----------|-------------|
| VITE_BACKEND_URL | Backend API URL |
| VITE_ENABLE_PAT | Enable personal access tokens |

## 20. Module Documentation

Each module has dedicated README files for detailed documentation.

### Documentation Location

| Level | Backend | Frontend |
|-------|---------|----------|
| Module | `backend/app/modules/{module}/README.md` | `frontend/src/modules/{module}/README.md` |
| Feature | — | `frontend/src/modules/{module}/{feature}/README.md` |

### Module Documentation Template

**Backend module README:**
```markdown
# {Module} Module

## Purpose
...

## Key Files
- models.py
- schemas.py
- service.py
- router.py

## API Endpoints
...

## End-to-End Flow
...

## Related Modules
...
```

**Frontend module/feature README:**
```markdown
# {Module} / {Feature}

## Purpose
...

## Key Files
...

## Store
...

## Pages
...

## End-to-End Flow
...

## Related Modules
...
```

## 21. README Update Workflow

After any action that modifies code structure or flow, proactively suggest updating relevant README files:

> "The [module/feature] README should be updated due to [changes]. Should I update it?"

### Triggers for Suggestion

| Change Type | Example |
|-------------|---------|
| New endpoint | Added `POST /device/sync` endpoint |
| New model/table | Created `DeviceTaskLog` model |
| New page or store | Added `DiscoveryPage.tsx` |
| New feature | Added bulk sync feature |
| Flow/dependency changes | Callback flow modified |
| API contract changes | Schema field added/removed |

### Scope

This applies to **all modules** — both backend (`app/modules/{module}/README.md`) and frontend (`src/modules/{module}/README.md`, `src/modules/{module}/{feature}/README.md`).

### Note

README files are located alongside their modules/features:
- Backend: `backend/app/modules/{module}/README.md`
- Frontend module: `frontend/src/modules/{module}/README.md`
- Frontend feature: `frontend/src/modules/{module}/{feature}/README.md`

## 22. Backend Type Safety Rules

### Timestamp Fields (created_at / updated_at)

**NEVER** declare timestamp model columns as `Mapped[str]` — SQLAlchemy `DateTime` columns return `datetime` objects regardless of type annotation.

**Correct pattern:**
```python
# models.py
from datetime import datetime
from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

class MyModel(Base):
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

# schemas.py
from datetime import datetime
from pydantic import BaseModel

class MyModelResponse(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}
```

**Incorrect pattern** (causes Pydantic ValidationError at runtime):
```python
# WRONG — model declares Mapped[str] but SQLAlchemy returns datetime
created_at: Mapped[str] = mapped_column(DateTime(timezone=True), ...)

# WRONG — schema expects str but receives datetime from model
created_at: str
```

**Why this matters:**
- `Mapped[str]` is only a type hint — SQLAlchemy ignores it and returns Python `datetime` for `DateTime` columns
- Pydantic's `from_attributes=True` performs strict validation and rejects `datetime → str` coercion
- Bug surfaces only at runtime when data exists in the table (silent until then)

**Rule of thumb:** Match the SQLAlchemy column type, not the annotation:

| Column Type | Python Type | Schema Type |
|-------------|-------------|-------------|
| `DateTime` | `datetime` | `datetime` |
| `JSON` | `dict` / `list` | `dict` / `list` |
| `String` | `str` | `str` |
| `Integer` | `int` | `int` |
| `Boolean` | `bool` | `bool` |
