# Dashboard module

The dashboard is the authenticated `/dashboard` landing page for read-only Luna attendance analytics. Its module manifest requires the exact `analytics:read` permission through the existing route and sidebar guards.

## Data flow

`DashboardPage` composes filters, KPIs, the trend chart, employee ranking, attendance exceptions, and shared panel states. It starts one bounded request for each backend dashboard resource: `/api/v1/dashboard/overview`, `/api/v1/dashboard/work-hours/trend`, `/api/v1/dashboard/work-hours/ranking`, and `/api/v1/dashboard/attendance-exceptions`. `store.ts` owns draft and applied filters, independent panel states, retries, request cancellation, and a generation guard that prevents stale responses from replacing newer results. Typing in a filter does not issue requests; Apply promotes the draft and reloads all panels.

Trend granularity reloads only the trend. Exception page and page-size controls reload only the exception table. Reset restores the backend defaults and omits optional dates and organization from the query string.

All requests use the OpenAPI-generated SDK from `src/api/generated`. The initial request omits dates so Luna determines the effective source range, which the page then displays. Durations remain integer seconds in state and are converted only for localized display. The module does not query Luna or raw clocks directly, calculate official work hours, or use polling, server-sent events, or WebSockets.

## UI and accessibility

- KPI cards show employee, duration, report-day, and exception totals.
- The responsive D3 trend chart uses theme tokens, translated units, pointer tooltips, and a screen-reader table with keyboard-focusable periods.
- Ranking and exception data use semantic tables with horizontal containment on narrow screens.
- Each panel has independent loading, empty, unavailable, generic-error, and retry rendering.
- English/Arabic, LTR/RTL, light/dark themes, and reduced-motion preferences are supported.
- Exceptions remain deliberately generic: the UI presents no inferred reason and no photo or internal-source field.

## Tests

`tests/dashboard/dashboard.spec.ts` intercepts authentication and all four dashboard routes. It covers initial loading, omitted default dates, draft/apply/reset behavior, organization scope, section-only granularity and paging calls, missing enrichment, empty and unavailable responses, partial failures, sanitized errors, Arabic RTL, dark theme, and mobile layout.

Production release still requires validation of real Luna field semantics and real SQL Server connectivity; those deployment gates are outside this frontend task.
