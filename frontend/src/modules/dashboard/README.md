# Dashboard module

The dashboard is the authenticated `/dashboard` landing page for read-only PostgreSQL attendance analytics. Its module manifest requires the exact `analytics:read` permission through the existing route and sidebar guards.

## Data flow

`DashboardPage` composes filters, KPIs, an employee comparison chart, employee ranking, attendance exceptions, and shared panel states. The chart requests `include_all=true` from the existing ranking endpoint so every filtered employee is shown, while the detailed ranking table retains its independently limited top-N response. Both use the same backend calculation and ordering. `store.ts` owns draft and applied filters, independent panel states, retries, and section-scoped request IDs/controllers that prevent stale responses without interrupting unrelated panels. Department options load independently on initialization and Refresh, not on Apply. Typing or selecting a draft filter does not issue analytics requests; Apply validates and promotes the draft, then reloads the dashboard analytics resources.

Ranking limit reloads the shared comparison chart/table data, and exception page/page-size controls reload only exceptions. An inverted date range is rejected locally before requests. Reset clears validation and restores backend defaults, omitting optional dates and department from the query string. The compatible trend API remains available but is no longer requested by this page.

The chart period selector defaults to Week and offers Day, Week, Month, and Year.
Changing it reloads only the all-employee comparison request; the backend derives
the real period scope from the effective global range. It does not reload or
change the independently limited ranking table.

The Department control contains dynamically loaded active departments. `ALL` is the default and means the `department_id` parameter is omitted. A failed department-options request leaves `ALL` usable.

All requests use the OpenAPI-generated SDK from `src/api/generated`. The initial request omits dates so PostgreSQL attendance data determines the effective source range, which the page then displays. Durations remain integer seconds in state and are converted only for localized display. The module does not use polling, server-sent events, or WebSockets.

Dashboard analytics requests are intentionally bounded to a maximum 366-day
range for the PostgreSQL V1 implementation. The backend also resolves the
default latest attendance date from a bounded recent event-time window and
applies active Timing working-day rules before choosing the effective date.

## UI and accessibility

- KPI cards show employee, duration, report-day, and exception totals.
- The responsive D3 horizontal grouped bar chart compares scheduled, actual, and overtime hours by employee in ranking order. It uses readable horizontal employee labels, theme tokens, translated units, keyboard/pointer tooltips, and bounded vertical scrolling for larger result sets.
- Ranking and exception data use semantic tables with horizontal containment on narrow screens.
- Each panel has independent loading, empty, unavailable, generic-error, and retry rendering.
- English/Arabic, LTR/RTL, light/dark themes, and reduced-motion preferences are supported.
- Exceptions remain deliberately generic: the UI presents no inferred reason and no photo or internal-source field.
- Attendance dates are grouped in `Asia/Dubai`. Exception `clock_time` preserves the computed Dubai-local event time returned by the API.

## Tests

`tests/dashboard/dashboard.spec.ts` intercepts authentication and dashboard routes. It covers employee-name fallback, all three bar series, tooltip values, shared chart/table filtering, stale responses, empty/unavailable states, English/Arabic, LTR/RTL, light/dark themes, and desktop/tablet/mobile layouts.

Known v1 limitations: no overnight shifts, multiple shifts, grace periods, breaks, holiday calendar, or effective-dated Timing history. Changing a Timing can recalculate historical dashboard output.
