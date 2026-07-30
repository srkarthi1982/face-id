# Shared Dialog Components

This directory contains reusable dialog components used across the application.

## CreateLocationChainDialog

Dialog for creating hierarchical location chains (Emirate → Base → Location → Building → Area).

### Location

`src/infra/shared/components/CreateLocationChainDialog.tsx`

### Features

- Multi-level location hierarchy creation
- Select existing or create new locations at each level
- Conditional display of levels (Base shows after Emirate selection, etc.)
- Form validation and error handling
- Unsaved changes confirmation
- **Configurable close behavior** (backdrop click and ESC key)

### Props

```typescript
interface CreateLocationChainDialogProps {
    isOpen: boolean;                              // Control dialog visibility
    onClose: () => void;                          // Close handler
    onSubmit: (chain: LocationChain) => void;    // Submit handler with chain data
    existingEmirates: LocationItem[];            // Available emirates for selection
    existingBases: LocationItem[];               // Available bases for selection
    existingLocations: LocationItem[];           // Available locations for selection
    existingBuildings: LocationItem[];           // Available buildings for selection
    existingAreas: LocationItem[];               // Available areas for selection
    closeOnBackdropClick?: boolean;              // Enable backdrop click and ESC key to close (default: false)
}
```

### Usage

```tsx
// Default - doesn't close on backdrop click or ESC (RECOMMENDED for complex forms)
<CreateLocationChainDialog
    isOpen={showChainDialog}
    onClose={() => setShowChainDialog(false)}
    onSubmit={handleChainSubmit}
    existingEmirates={emirates}
    existingBases={bases}
    existingLocations={locations}
    existingBuildings={buildings}
    existingAreas={areas}
/>

// Opt-in - closes on backdrop click and ESC key (for simpler workflows)
<CreateLocationChainDialog
    isOpen={showChainDialog}
    onClose={() => setShowChainDialog(false)}
    onSubmit={handleChainSubmit}
    closeOnBackdropClick={true}  // ← Enables both backdrop click and ESC key
    existingEmirates={emirates}
    existingBases={bases}
    existingLocations={locations}
    existingBuildings={buildings}
    existingAreas={areas}
/>
```

### Behavior

**When `closeOnBackdropClick = false` (default):**
- ❌ Clicking outside dialog does NOT close it
- ❌ Pressing ESC key does NOT close it
- ✅ Must use close button (X) or Cancel button
- ✅ Prevents accidental data loss in complex forms

**When `closeOnBackdropClick = true`:**
- ✅ Clicking outside dialog closes it (with unsaved changes confirmation)
- ✅ Pressing ESC key closes it (with unssaved changes confirmation)
- ✅ Close button (X) still works
- ✅ Cancel button still works

### Related Components

- `LocationPage` - Main location management page that uses this dialog
- `SearchableCombobox` - Used within the dialog for location selection

---

## CreateUnitChainDialog

Dialog for creating hierarchical unit chains (Force → Command → Battalion → Unit).

### Location

`src/infra/shared/components/CreateUnitChainDialog.tsx`

### Features

- Multi-level unit hierarchy creation
- Select existing or create new units at each level
- Code-based search and creation
- Conditional display of levels (Command shows after Force selection, etc.)
- Form validation and error handling
- Unsaved changes confirmation
- **Configurable close behavior** (backdrop click and ESC key)

### Props

```typescript
interface CreateUnitChainDialogProps {
    isOpen: boolean;                              // Control dialog visibility
    onClose: () => void;                          // Close handler
    onSubmit: (chain: UnitChain) => void;        // Submit handler with chain data
    existingForces: UnitItem[];                  // Available forces for selection
    existingCommands: UnitItem[];                // Available commands for selection
    existingBattalions: UnitItem[];              // Available battalions for selection
    existingUnits: UnitItem[];                   // Available units for selection
    closeOnBackdropClick?: boolean;              // Enable backdrop click and ESC key to close (default: false)
}
```

### Usage

```tsx
// Default - doesn't close on backdrop click or ESC (RECOMMENDED)
<CreateUnitChainDialog
    isOpen={showChainDialog}
    onClose={() => setShowChainDialog(false)}
    onSubmit={handleChainSubmit}
    existingForces={forces}
    existingCommands={commands}
    existingBattalions={battalions}
    existingUnits={units}
/>

// Opt-in - closes on backdrop click and ESC key
<CreateUnitChainDialog
    isOpen={showChainDialog}
    onClose={() => setShowChainDialog(false)}
    onSubmit={handleChainSubmit}
    closeOnBackdropClick={true}  // ← Enables both backdrop click and ESC key
    existingForces={forces}
    existingCommands={commands}
    existingBattalions={battalions}
    existingUnits={units}
/>
```

### Behavior

**When `closeOnBackdropClick = false` (default):**
- ❌ Clicking outside dialog does NOT close it
- ❌ Pressing ESC key does NOT close it
- ✅ Must use close button (X) or Cancel button
- ✅ Prevents accidental data loss in complex forms

**When `closeOnBackdropClick = true`:**
- ✅ Clicking outside dialog closes it (with unsaved changes confirmation)
- ✅ Pressing ESC key closes it (with unsaved changes confirmation)
- ✅ Close button (X) still works
- ✅ Cancel button still works

### Related Components

- `UnitPage` - Main unit management page that uses this dialog
- `SearchableCombobox` - Used within the dialog for unit selection (code-based search)

---

## Design Decisions

### Why `closeOnBackdropClick` defaults to `false`?

1. **Data Protection**: Both dialogs handle complex multi-step forms. Accidental closure could result in significant data loss.

2. **User Intent**: Requiring explicit action (clicking Cancel or X button) ensures the user intentionally wants to close the dialog.

3. **Modern UX Pattern**: Leading productivity tools (Linear, Notion, Stripe) use conservative close behavior for complex forms.

4. **Flexibility**: Developers can opt-in to backdrop closing for simpler use cases where data loss is less critical.

### ESC Key Behavior

The ESC key is tied to the same `closeOnBackdropClick` parameter because:

1. **Consistency**: Both are "quick exit" mechanisms that should behave the same way
2. **Predictability**: Users expect ESC and backdrop click to have the same effect
3. **Simplicity**: Single parameter is easier to understand than separate controls

### Unsaved Changes Confirmation

When `closeOnBackdropClick = true`, the dialog still shows a confirmation prompt if there are unsaved changes:

```typescript
if (state.hasUnsavedChanges) {
    const confirmed = window.confirm('You have unsaved changes. Discard?');
    if (!confirmed) return;
}
```

This provides an additional safety net even when quick-close is enabled.

---

## Testing Checklist

- [ ] Dialog opens correctly with `isOpen={true}`
- [ ] Close button (X) works regardless of `closeOnBackdropClick` setting
- [ ] Cancel button works regardless of `closeOnBackdropClick` setting
- [ ] With `closeOnBackdropClick={false}` (default):
  - [ ] Clicking backdrop does NOT close dialog
  - [ ] Pressing ESC does NOT close dialog
- [ ] With `closeOnBackdropClick={true}`:
  - [ ] Clicking backdrop closes dialog
  - [ ] Pressing ESC closes dialog
  - [ ] Unsaved changes confirmation appears when applicable
- [ ] Form validation works correctly
- [ ] Chain creation submits correct data structure

---

## Related Documentation

- [Master Module Documentation](../../../modules/master/README.md)
- [Location Module Documentation](../../../modules/master/location/README.md)
- [Unit Module Documentation](../../../modules/master/unit/README.md)
- [SearchableCombobox Component](./SearchableCombobox.tsx)
