# Dashboard module

The dashboard is the authenticated `/dashboard` landing page for read-only Luna attendance analytics. Its module manifest requires the exact `analytics:read` permission through the existing route and sidebar guards.

## Data flow

`DashboardPage` composes filters, KPIs, the trend chart, employee ranking, attendance exceptions, and shared panel states. It starts one bounded request for each analytics resource plus `/api/v1/dashboard/organizations`. `store.ts` owns draft and applied filters, independent panel states, retries, and section-scoped request IDs/controllers that prevent stale responses without interrupting unrelated panels. Organization options load independently on initialization and Refresh, not on Apply. Typing or selecting a draft filter does not issue analytics requests; Apply validates and promotes the draft, then reloads the four analytics panels.

Trend granularity reloads only the trend, ranking limit reloads only ranking, and exception page/page-size controls reload only exceptions. An inverted date range is rejected locally before requests. Reset clears validation and restores backend defaults, omitting optional dates and organization from the query string.

The Organization control contains dynamically loaded, sorted Luna organization IDs. `ALL` is the default and means the `org_id` parameter is omitted. The supplied Luna contract has no organization-name table, so no display names are inferred or hardcoded. A failed organization-options request leaves `ALL` usable.

All requests use the OpenAPI-generated SDK from `src/api/generated`. The initial request omits dates so Luna determines the effective source range, which the page then displays. Durations remain integer seconds in state and are converted only for localized display. The module does not query Luna or raw clocks directly, calculate official work hours, or use polling, server-sent events, or WebSockets.

## UI and accessibility

- KPI cards show employee, duration, report-day, and exception totals.
- The responsive D3 trend chart uses theme tokens, translated units, pointer tooltips, and a screen-reader table with keyboard-focusable periods.
- Ranking and exception data use semantic tables with horizontal containment on narrow screens.
- Each panel has independent loading, empty, unavailable, generic-error, and retry rendering.
- English/Arabic, LTR/RTL, light/dark themes, and reduced-motion preferences are supported.
- Exceptions remain deliberately generic: the UI presents no inferred reason and no photo or internal-source field.
- Luna `report_date` values are formatted as date-only values without timezone conversion. Exception `clock_time` preserves the returned source wall clock; timezone conversion remains intentionally deferred until production Luna timezone semantics are confirmed.

## Tests

`tests/dashboard/dashboard.spec.ts` intercepts authentication and all five dashboard routes. It covers organization loading/failure/race safety, initial loading, omitted default dates, draft/apply/reset behavior, organization scope, ranking-header layout, section-only controls, missing enrichment, three recent exceptions, empty and unavailable responses, partial failures, sanitized errors, Arabic RTL, dark theme, and mobile layout.

Production release still requires validation of real Luna field semantics and real SQL Server connectivity; those deployment gates are outside this frontend task.
