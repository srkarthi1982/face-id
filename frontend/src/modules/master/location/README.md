# Location Feature

## Purpose

Provides UI for managing hierarchical location data. Users can create, view, edit, and delete locations in a geographic/physical hierarchy.

## Key Files

- `LocationPage.tsx` — Main CRUD page with tree table view
- `store.ts` — Zustand store for location state management
- `manifest.ts` — Feature configuration (path, i18n, page component)

## Store

Uses `useLocationStore` with:
- `treeItems`: Nested location tree for hierarchical display
- `flatItems`: Flat array of all locations
- `itemsByType`: Locations grouped by type (emirate, base, location, building, area)
- `commandUnits`: List of command-level units for assignment
- `selectedUnitId`: Currently selected unit for filtering
- `fetchTree(unitId?)`: Fetch location tree, optionally filtered by unit
- `fetchByType(type)`: Fetch locations of specific type
- `create()`, `update()`, `remove()`: CRUD operations
- `createWithFullChain()`: Create full location chain in one operation

## Pages

### LocationPage
- **Tree table**: Displays locations in hierarchical tree structure
- **Expand/collapse**: Toggle visibility of child locations
- **CRUD actions**: Create, edit, delete buttons per row
- **Type badges**: Shows location type (emirate, base, etc.)
- **Unit filtering**: Filter tree by selected unit
- **Alphabetical sorting**: All levels sorted by name

## End-to-End Flow

### Viewing Location Tree
1. Page loads, calls `fetchTree()`
2. Backend returns sorted tree (by name at all levels)
3. Store processes tree structure (preserves order)
4. Component renders tree table
5. User can expand/collapse nodes

### Creating Location
1. User clicks "Create Location" button
2. Dialog opens with form fields (name, type, parent, unit)
3. User fills form and submits
4. Frontend calls `createLocation()` API
5. Backend saves and computes path
6. Frontend refreshes tree and flat list
7. New location appears in correct alphabetical position

### Creating Location Chain
1. User clicks "Create with Full Chain" button
2. Dialog opens with chain input (Emirate → Base → Location → Building → Area)
3. User enters full chain
4. Frontend calls `createLocationWithFullChain()` API
5. Backend creates all levels with proper parent relationships
6. Frontend refreshes tree
7. All new locations appear in correct positions

## Sorting

Frontend does NOT re-sort. Backend returns:
- Root locations sorted by name
- Children sorted by name at each level
- Type-filtered lists sorted by name

Store simply processes tree structure:
```typescript
const processTreeItems = (items: LocationItem[]): LocationItem[] => {
    return items.map(item => ({
        ...item,
        children: item.children ? processTreeItems(item.children) : undefined,
    }))
}
```

## Related Features

- `unit` — Units can be assigned to locations
- `device` — Devices can be assigned to locations
