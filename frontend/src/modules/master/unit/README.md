# Unit Feature

## Purpose

Provides UI for managing hierarchical organizational unit data. Users can create, view, edit, and delete units in a Force → Command → Battalion → Unit hierarchy.

## Key Files

- `UnitPage.tsx` — Main CRUD page with tree table view
- `store.ts` — Zustand store for unit state management
- `manifest.ts` — Feature configuration (path, i18n, page component)

## Store

Uses `useUnitStore` with:
- `treeItems`: Nested unit tree for hierarchical display
- `flatItems`: Flat array of all units
- `itemsByType`: Units grouped by type (force, command, battalion, unit)
- `fetchTree()`: Fetch full unit tree
- `fetchByType(type)`: Fetch units of specific type
- `create()`, `update()`, `remove()`: CRUD operations
- `createWithFullChain()`: Create full unit chain in one operation

## Pages

### UnitPage
- **Tree table**: Displays units in hierarchical tree structure
- **Expand/collapse**: Toggle visibility of child units
- **CRUD actions**: Create, edit, delete buttons per row
- **Type badges**: Shows unit type (force, command, battalion, unit)
- **Code-based sorting**: Children sorted by code (primary), then name (secondary)
- **Chain creation**: Create full hierarchy in one operation

## End-to-End Flow

### Viewing Unit Tree
1. Page loads, calls `fetchTree()`
2. Backend returns sorted tree (root by name, children by code then name)
3. Store processes tree structure (preserves order)
4. Component renders tree table
5. User can expand/collapse nodes

### Creating Unit
1. User clicks "Create Unit" button
2. Dialog opens with form fields (name, code, type, parent, description)
3. User fills form and submits
4. Frontend calls `createUnit()` API
5. Backend saves and computes path
6. Frontend refreshes tree and flat list
7. New unit appears in correct sorted position (by code)

### Creating Unit Chain
1. User clicks "Create Unit" button (chain dialog)
2. Dialog opens with chain input (Force → Command → Battalion → Unit)
3. User enters full chain
4. Frontend calls `createUnitWithFullChain()` API
5. Backend creates all levels with proper parent relationships
6. Frontend refreshes tree and all type groups
7. All new units appear in correct sorted positions

## Sorting

Frontend does NOT re-sort. Backend returns:
- Root units sorted by name
- Children sorted by code (primary), then name (secondary)
- Type-filtered lists sorted by name

Store simply processes tree structure:
```typescript
const processTreeItems = (items: UnitItem[]): UnitItem[] => {
    return items.map(item => ({
        ...item,
        children: item.children ? processTreeItems(item.children) : undefined,
    }))
}
```

**Important**: The sorting logic is in backend (`service.py`):
```python
children=[build_tree(child) for child in sorted(unit.children, key=lambda x: (x.code or '', x.name))]
```

This ensures consistent sorting across all clients (web, mobile, API consumers).

## Enum Values

Unit types are lowercase:
- `force` — Top-level organizational unit
- `command` — Second-level command structure
- `battalion` — Third-level battalion structure
- `unit` — Fourth-level unit

## Related Features

- `location` — Locations can be assigned to units
- `device` — Devices can be assigned to units
- `settings/access-management` — Manages unit:read/write permissions
