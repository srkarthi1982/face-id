# Frontend Agent Instructions - Personnel Module

## Context
You are assisting the frontend developer implementing the Personnel module for the JAC Face ID Management System.

## Implementation Plan
**Primary Reference:** `.opencode/plans/personnel-module-implementation.md`

## Before Starting Each Session
1. Read `.opencode/progress-log.md` to see current status
2. Check latest git commits: `git log -5 --oneline`
3. Review `frontend/src/modules/personnel/` for current state
4. Identify which Track to work on (2.1 → 2.2 → 2.3 → 2.4)

## During Session
1. Follow the implementation plan tracks in order
2. Run `npm run type-check` after each file change
3. Commit every 30-60 minutes with structured messages
4. Test in browser after completing each page

## Git Commit Message Format
```
personnel: [Track X.X] <description>
<details>

Progress: Day X/10 - Frontend Track X.X <STATUS>
```

**Example:**
```
personnel: [Track 2.1] Create Zustand store
- Implement usePersonnelStore using createCrudStore factory
- Import API functions from generated client
- Wire up listApi, createApi, updateApi, deleteApi

Progress: Day 1/10 - Frontend Track 2.1 COMPLETE ✅
```

## After Each Session
1. Commit all work (even if incomplete - use "WIP:" prefix)
2. Update `.opencode/progress-log.md` with:
   - Track number and status
   - What was completed
   - Files modified
   - Any blockers
   - Next session plan
3. Leave notes in session file if mid-track

## Session File Template
Create: `.opencode/sessions/frontend-YYYY-MM-DD.md`
```markdown
# Frontend Session - YYYY-MM-DD
**Developer:** [Name]
**Track:** X.X - <Track Name>
**Status:** COMPLETE / IN PROGRESS / BLOCKED

## Goal
<What you planned to accomplish>

## Completed
- [ ] Task 1
- [ ] Task 2

## Files Modified
- `frontend/src/modules/personnel/file.tsx`

## Issues/Blockers
<Any issues encountered>

## Next Session
<What to work on next>
```

## Testing Commands
```bash
# Type check (run frequently)
cd frontend
npm run type-check

# Dev server
npm run dev

# Build test (pre-push)
npm run build

# Generate types (if backend changed)
npm run generate-types
```

## Key Files Reference
- Store: `frontend/src/modules/personnel/store.ts`
- List Page: `frontend/src/modules/personnel/PersonnelListPage.tsx`
- Translations: `frontend/src/infra/locales/en.json` & `ar.json`
- CrudPage: `frontend/src/infra/shared/components/CrudPage.tsx`
- Store Factory: `frontend/src/infra/shared/utils/createCrudStore.ts`
- API Client: `frontend/src/api/generated.ts`

## Integration Points
- API Client → Auto-generated from backend
- Translations → Must update both en.json and ar.json
- Theme → Must support light/dark modes
- Permissions → Must respect PERSONNEL_READ/WRITE

## Critical Rules
1. **ALWAYS** import `'../../../api/client'` first in store files
2. **ALWAYS** use `useShallow` hook when consuming store
3. **ALWAYS** run type-check after file changes
4. **NEVER** hardcode colors - use CSS variables
5. **NEVER** add root padding to pages (Layout owns margins)

## When Blocked
1. Check existing modules for patterns (e.g., `device-management/`)
2. Review `CrudPage.tsx` for component API
3. Consult progress log for backend developer status
4. Ask for clarification via developer
