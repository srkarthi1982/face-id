# Master Module

## Purpose

Provides UI for managing hierarchical master data: Locations and Units. This module enables users to:
- **Manage locations**: Create, edit, and delete geographic/physical locations in a hierarchy
- **Manage units**: Create, edit, and delete organizational units (Force/Command/Battalion/Unit)
- **View sorted trees**: All trees display alphabetically (locations by name, units by code then name)
- **Assign units to locations**: Link supervising units to locations
- **Filter by type**: View locations and units filtered by their type

## Key Files

- `api.ts` — API client functions for backend communication
- `types.ts` — TypeScript type definitions for Location and Unit
- `manifest.ts` — Module configuration (path, icon, order)
- `location/` — Location management feature
  - `LocationPage.tsx` — Main location CRUD page with tree view
  - `store.ts` — Zustand store for location state
  - `manifest.ts` — Location feature configuration
- `unit/` — Unit management feature
  - `UnitPage.tsx` — Main unit CRUD page with tree view
  - `store.ts` — Zustand store for unit state
  - `manifest.ts` — Unit feature configuration

## Module Structure

```
master/
├── manifest.ts                 # Module manifest
├── types.ts                    # Shared types
├── api.ts                      # API client
├── location/
│   ├── manifest.ts            # Location feature manifest
│   ├── LocationPage.tsx       # Location CRUD page
│   └── store.ts               # Location store
└── unit/
    ├── manifest.ts            # Unit feature manifest
    ├── UnitPage.tsx           # Unit CRUD page
    └── store.ts               # Unit store
```

## Features

### Location Management
- **Tree view**: Hierarchical display of locations (Emirate → Base → Location → Building → Area)
- **CRUD operations**: Create, read, update, delete locations
- **Type filtering**: View locations by type (all emirates, all bases, etc.)
- **Unit assignment**: Assign supervising units to locations
- **Alphabetical sorting**: All levels sorted by name
- **Chain creation**: Create full location chains in one operation

### Unit Management
- **Tree view**: Hierarchical display of units (Force → Command → Battalion → Unit)
- **CRUD operations**: Create, read, update, delete units
- **Type filtering**: View units by type (all forces, all commands, etc.)
- **Code-based sorting**: Children sorted by code (primary), then name (secondary)
- **Chain creation**: Create full unit chains in one operation

## Store Pattern

Both location and unit features use Zustand stores with:
- `treeItems`: Nested tree structure for hierarchical display
- `flatItems`: Flat array for table/list views
- `itemsByType`: Grouped items by type for filtering
- `fetchTree()`: Fetch nested tree from backend
- `fetch()`: Fetch flat list
- `fetchByType(type)`: Fetch items filtered by type
- `create()`, `update()`, `remove()`: CRUD operations

## API Integration

All API calls use the generated client from `@hey-api/client-fetch`:
- **Backend sorting**: Backend handles all sorting, frontend preserves order
- **Type safety**: TypeScript types match backend schemas
- **Error handling**: Uses `throwIfError()` for consistent error handling

## Sorting Behavior

Frontend preserves backend sorting:
- **Location tree**: Sorted by name at all levels (backend: `order_by(Location.name)`)
- **Unit tree**: Root sorted by name, children sorted by code then name (backend: `sorted(children, key=lambda x: (x.code or '', x.name))`)
- **No frontend re-sorting**: Store simply processes tree structure without modifying order

## Enum Values

### LocationType (lowercase)
- `emirate`, `base`, `location`, `building`, `area`

### UnitType (lowercase)
- `force`, `command`, `battalion`, `unit`

## Related Modules

- `device` — Devices can be assigned to locations and units
- `settings/access-management` — Manages permissions for master data (location:read/write, unit:read/write)

## End-to-End Flow

### Creating a Location
1. User clicks "Create Location" button
2. Dialog opens with parent selection dropdown
3. User selects parent and enters name
4. Frontend calls `createLocation()` API
5. Backend computes path and saves location
6. Frontend refreshes tree and flat list
7. Tree displays new location in alphabetical order

### Creating a Unit Chain
1. User clicks "Create Unit" button
2. Dialog opens with chain input (Force → Command → Battalion → Unit)
3. User enters full chain
4. Frontend calls `createUnitWithFullChain()` API
5. Backend creates all levels and computes paths
6. Frontend refreshes tree and items by type
7. Tree displays new units sorted by code/name

## Permissions

Access controlled by:
- `location:read` — View locations
- `location:write` — Create/update/delete locations
- `unit:read` — View units
- `unit:write` — Create/update/delete units

Permissions are checked in backend; frontend shows/hides actions based on user permissions.
