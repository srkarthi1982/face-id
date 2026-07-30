# Master Data Module

## Purpose

Provides hierarchical master data management for Locations and Units. This module enables:
- **Location hierarchy**: Geographic/physical locations with parent-child relationships
- **Unit hierarchy**: Organizational units (Force/Command/Battalion/Unit) with type classification
- **Unit assignment**: Locations can be assigned to supervising Units
- **Device assignment**: Devices can be assigned to both Locations and Units
- **Alphabetical sorting**: All tree endpoints return data sorted alphabetically (by name for locations, by code then name for units)

## Key Files

- `models.py` — Location and Unit models with self-referential hierarchies
- `schemas.py` — Pydantic schemas for CRUD operations and responses
- `service.py` — Business logic for hierarchy management, path computation, and sorting
- `router.py` — API endpoints under `/api/v1/master-data/`

## Data Models

### Location
- `id`: Primary key
- `name`: Location name
- `parent_id`: Self-referential FK for hierarchy
- `unit_id`: FK to Unit (optional supervising unit)
- `type`: Enum (emirate/base/location/building/area)
- `path`: Denormalized path string (e.g., "/Building A/Floor 2")
- `is_active`: Active flag
- `sort_order`: Display order

### Unit
- `id`: Primary key
- `name`: Unit name
- `code`: Unit code (unique under parent)
- `description`: Unit description
- `type`: Enum (force/command/battalion/unit)
- `parent_id`: Self-referential FK for hierarchy
- `path`: Denormalized path string
- `is_active`: Active flag
- `sort_order`: Display order

## API Endpoints

### Locations
```
GET    /api/v1/master-data/locations/tree              — Full nested tree (sorted by name)
GET    /api/v1/master-data/locations/tree?unit_id={id} — Filtered tree by unit
GET    /api/v1/master-data/locations                   — Flat list
GET    /api/v1/master-data/locations/{id}              — Single location
GET    /api/v1/master-data/locations/by-type/{type}    — Locations by type (sorted by name)
GET    /api/v1/master-data/locations/valid-parents/{type} — Valid parents for location type
POST   /api/v1/master-data/locations                   — Create location
PUT    /api/v1/master-data/locations/{id}              — Update location
DELETE /api/v1/master-data/locations/{id}              — Delete location (409 if referenced)
```

### Units
```
GET    /api/v1/master-data/units/tree                  — Full nested tree (sorted by code, then name)
GET    /api/v1/master-data/units                       — Flat list
GET    /api/v1/master-data/units/{id}                  — Single unit
GET    /api/v1/master-data/units/by-type/{type}        — Units by type (sorted by name)
GET    /api/v1/master-data/units/valid-parents/{type}  — Valid parents for unit type
POST   /api/v1/master-data/units                       — Create unit
PUT    /api/v1/master-data/units/{id}                  — Update unit
DELETE /api/v1/master-data/units/{id}                  — Delete unit (409 if referenced)
```

## Hierarchy Path Computation

Paths are automatically computed and updated:
- When creating: path = parent.path + "/" + name
- When updating parent/name: cascade updates all children paths
- Path format: "/Root/Child/Grandchild"

## Sorting Behavior

All tree and list endpoints return data sorted alphabetically:
- **Unit tree**: Root units sorted by name, children sorted by code (primary) then name (secondary)
- **Location tree**: All levels sorted by name
- **Type-filtered lists**: Sorted by name (e.g., `/by-type/force`, `/by-type/emirate`)
- **Valid parents**: Sorted by name

## Constraints

- **Location**: Cannot delete if has children or referenced by devices
- **Unit**: Cannot delete if has children, referenced by locations, or referenced by devices
- **Unit code**: Unique constraint on (parent_id, code)

## Enum Values

### LocationType
- `emirate`, `base`, `location`, `building`, `area`

### UnitType
- `force`, `command`, `battalion`, `unit`

**Note**: All enum values are lowercase for consistency.

## Related Modules

- `device` — Devices reference locations and units via FKs
- `permissions` — Defines location:read/write and unit:read/write permissions
