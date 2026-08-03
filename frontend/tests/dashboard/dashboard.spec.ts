import { expect, test, type Page, type Route } from '@playwright/test'

const duration = { scheduled_seconds: 32_400, actual_seconds: 30_600, normal_seconds: 28_800, overtime_seconds: 1_800, late_seconds: 300, early_seconds: 0, absent_seconds: 0 }
const range = { effective_start_date: '2026-07-01', effective_end_date: '2026-07-30', source_latest_report_date: '2026-07-30', department_id: null, data_status: 'available', duration_unit: 'seconds' }
const overview = { ...range, ...duration, report_row_count: 22, report_day_count: 20, employee_count: 7, reported_exception_count: 3 }
const ranking = [
  { ...duration, rank: 1, department_id: 1, employee_key: 'P-01', person_id: 'P-01', person_no: 'E-01', person_name: 'Amina Noor', department_name: 'Operations', report_day_count: 20 },
  { ...duration, scheduled_seconds: 28_800, actual_seconds: 27_000, overtime_seconds: 0, rank: 2, department_id: 2, employee_key: 'E-02', person_id: null, person_no: 'E-02', person_name: null, department_name: 'International Operations and Workforce Planning Department', report_day_count: 18 },
  { ...duration, rank: 3, department_id: 2, employee_key: 'LONG-03', person_id: 'LONG-03', person_no: 'E-03', person_name: 'A very long employee name retained in full for accessibility', department_name: 'Operations', report_day_count: 17 },
]
const allEmployees = [
  ...ranking,
  ...Array.from({ length: 9 }, (_, index) => ({
    ...ranking[0], rank: index + 4, employee_key: `P-${index + 4}`,
    person_id: `P-${index + 4}`, person_no: `E-${index + 4}`,
    person_name: `Employee Beyond Ten ${index + 4}`,
    actual_seconds: ranking[0].actual_seconds - (index + 1) * 60,
  })),
]
const exception = { id: '1:2026-07-30:LATE', department_id: 1, department_name: 'Operations', exception_type: 'LATE', person_id: 'P-01', person_no: 'E-01', person_name: 'Amina Noor', report_date: '2026-07-30', clock_time: '2026-07-30T08:10:00+04:00', device_key: 'D-01', device_name: 'Main Gate' }
const departments = [
  { department_id: 1, department_name: 'Operations' },
  { department_id: 2, department_name: 'International Operations and Workforce Planning Department' },
  { department_id: 3, department_name: 'Research' },
  { department_id: 4, department_name: 'Support' },
  { department_id: 5, department_name: 'Training' },
]
const departmentByName = new Map(departments.map((department) => [department.department_name, String(department.department_id)]))
type Mode = 'available' | 'empty' | 'unavailable'

async function respond(route: Route, mode: Mode) {
  const url = new URL(route.request().url()); const path = url.pathname
  if (mode === 'unavailable') return route.fulfill({ status: 503, json: { detail: 'Attendance analytics are temporarily unavailable' } })
  const empty = mode === 'empty'
  if (path.endsWith('/departments')) return route.fulfill({ json: { success: true, data: departments } })
  if (path.endsWith('/overview')) return route.fulfill({ json: { success: true, data: empty ? { ...overview, data_status: 'empty', report_row_count: 0 } : overview } })
  if (path.endsWith('/work-hours/ranking')) return route.fulfill({ json: { success: true, data: { ...range, department_id: url.searchParams.get('department_id') ? Number(url.searchParams.get('department_id')) : null, items: empty ? [] : url.searchParams.get('include_all') === 'true' ? allEmployees : ranking } } })
  if (path.endsWith('/work-hours/trend')) return route.fulfill({ json: { success: true, data: { ...range, granularity: 'week', points: [] } } })
  return route.fulfill({ json: { success: true, data: empty ? [] : [exception], meta: { page: 1, page_size: 20, total: empty ? 0 : 1, pages: empty ? 0 : 1 } } })
}

async function mockApp(page: Page, mode: Mode = 'available') {
  await page.addInitScript(() => {
    localStorage.setItem('access_token', 'dashboard-test-token')
    if (!localStorage.getItem('lang')) localStorage.setItem('lang', 'en')
    if (!localStorage.getItem('theme')) localStorage.setItem('theme', 'light')
  })
  await page.route('**/api/v1/auth/me**', async (route) => {
    if (new URL(route.request().url()).pathname.endsWith('/permissions')) return route.fulfill({ json: { success: true, data: ['analytics:read'] } })
    return route.fulfill({ json: { success: true, data: { id: 1, email: 'dashboard@example.test', username: 'dashboard', roles: ['viewer'], auth_provider: 'local', created_at: '2026-01-01T00:00:00Z', updated_at: '2026-01-01T00:00:00Z', version: 1 } } })
  })
  await page.route('**/api/v1/dashboard/**', async (route) => respond(route, mode))
}

test('renders employee comparison bars, names, tooltips, and the ranking table', async ({ page }) => {
  await mockApp(page); const requests: URL[] = []
  page.on('request', (request) => { if (request.url().includes('/api/v1/dashboard/')) requests.push(new URL(request.url())) })
  await page.goto('/dashboard')
  await expect(page.getByRole('heading', { name: 'Employee work-hours comparison' })).toBeVisible()
  await expect(page.getByLabel('Chart period')).toHaveValue('week')
  await expect(page.getByTestId('employee-chart-name')).toHaveCount(12)
  await expect(page.getByTestId('employee-chart-name').filter({ hasText: 'Amina Noor' })).toBeVisible()
  await expect(page.getByTestId('employee-chart-name').filter({ hasText: 'E-02' })).toBeVisible()
  await expect(page.getByTestId('employee-chart-name').filter({ hasText: 'Employee Beyond Ten 12' })).toBeVisible()
  for (const name of ['scheduled', 'actual', 'overtime']) await expect(page.locator(`rect[data-series="${name}"]`)).toHaveCount(12)
  const scheduled = page.locator('rect[data-series="scheduled"]').first(); await scheduled.focus()
  await expect(page.getByRole('tooltip')).toContainText('Amina Noor'); await expect(page.getByRole('tooltip')).toContainText('9 h')
  await expect(page.getByRole('heading', { name: 'Employee work-hours ranking' })).toBeVisible()
  await expect(page.getByRole('cell', { name: 'Amina Noor' }).first()).toBeVisible()
  await expect(page.getByRole('cell', { name: 'Employee Beyond Ten 12' })).toHaveCount(0)
  expect(requests.some((url) => url.pathname.endsWith('/work-hours/trend'))).toBeFalsy()
})

test('keeps names horizontal, preserves full long names accessibly, and scrolls many rows', async ({ page }) => {
  await mockApp(page); await page.goto('/dashboard')
  const names = page.getByTestId('employee-chart-name')
  expect(await names.evaluateAll((nodes) => nodes.every((node) => getComputedStyle(node).writingMode === 'horizontal-tb'))).toBeTruthy()
  await expect(page.locator('rect[aria-label^="A very long employee name retained in full for accessibility"]')).toHaveCount(3)
  await expect(page.getByTestId('employee-comparison-scroll')).toHaveCSS('overflow-y', 'auto')
  const rows = page.getByTestId('employee-chart-row'); const first = await rows.nth(0).boundingBox(); const second = await rows.nth(1).boundingBox()
  expect(first && second && second.y - first.y >= 60).toBeTruthy()
})

test('global dates and department refresh the chart ranking request', async ({ page }) => {
  await mockApp(page); const requests: URL[] = []
  page.on('request', (request) => { if (request.url().includes('/work-hours/ranking')) requests.push(new URL(request.url())) })
  await page.goto('/dashboard'); await expect(page.getByTestId('employee-chart-name')).toHaveCount(12); requests.length = 0
  await page.getByLabel('Start date').fill('2026-07-10'); await page.getByLabel('End date').fill('2026-07-20'); await page.getByLabel('Department').selectOption(departmentByName.get('International Operations and Workforce Planning Department')!)
  await page.getByRole('button', { name: 'Apply filters' }).click(); await expect.poll(() => requests.length).toBe(2)
  expect(requests.every((url) => url.searchParams.get('department_id') === departmentByName.get('International Operations and Workforce Planning Department') && url.searchParams.get('start_date') === '2026-07-10')).toBeTruthy()
  expect(requests.some((url) => url.searchParams.get('include_all') === 'true')).toBeTruthy()
})

test('Day Week Month Year genuinely rescope only the all-employee chart request', async ({ page }) => {
  await mockApp(page); const requests: URL[] = []
  page.on('request', (request) => { if (request.url().includes('/work-hours/ranking')) requests.push(new URL(request.url())) })
  await page.goto('/dashboard'); await expect(page.getByTestId('employee-chart-name')).toHaveCount(12); requests.length = 0
  const selector = page.getByLabel('Chart period')
  for (const period of ['day', 'month', 'year', 'week']) {
    await selector.selectOption(period); await expect.poll(() => requests.length).toBe(1)
    expect(requests[0].searchParams.get('period')).toBe(period)
    expect(requests[0].searchParams.get('include_all')).toBe('true')
    expect(requests[0].searchParams.has('limit')).toBeFalsy()
    await expect(page.getByTestId('employee-chart-name').filter({ hasText: 'Employee Beyond Ten 12' })).toBeVisible()
    await expect(page.getByLabel('Rows', { exact: true })).toHaveValue('10')
    requests.length = 0
  }
})

test('ranking limit refreshes the shared chart and table without losing draft department', async ({ page }) => {
  await mockApp(page); const requests: URL[] = []
  page.on('request', (request) => { if (request.url().includes('/work-hours/ranking')) requests.push(new URL(request.url())) })
  await page.goto('/dashboard'); await expect(page.getByRole('heading', { name: 'Employee work-hours ranking' })).toBeVisible(); await expect(page.getByRole('cell', { name: 'Amina Noor' }).first()).toBeVisible(); requests.length = 0
  await page.getByLabel('Department').selectOption(departmentByName.get('Training')!); await page.getByLabel('Rows', { exact: true }).selectOption('20')
  await expect.poll(() => requests.length).toBe(1); expect(requests[0].searchParams.get('limit')).toBe('20')
  await expect(page.getByLabel('Department')).toHaveValue(departmentByName.get('Training')!)
})

for (const viewport of [{ width: 360, height: 800 }, { width: 768, height: 900 }, { width: 1440, height: 1000 }]) {
  for (const lang of ['en', 'ar'] as const) for (const theme of ['light', 'dark'] as const) test(`${lang} ${theme} at ${viewport.width}px`, async ({ page }) => {
    await page.setViewportSize(viewport); await mockApp(page)
    await page.addInitScript(({ lang, theme }) => { localStorage.setItem('lang', lang); localStorage.setItem('theme', theme) }, { lang, theme })
    await page.goto('/dashboard'); await expect(page.locator('html')).toHaveAttribute('dir', lang === 'ar' ? 'rtl' : 'ltr'); await expect(page.locator('html')).toHaveAttribute('data-theme', theme)
    await expect(page.getByTestId('employee-chart-name').first()).toBeVisible()
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth)).toBeTruthy()
  })
}

test('empty, unavailable, and stale-request states remain isolated', async ({ page }) => {
  await mockApp(page, 'empty'); await page.goto('/dashboard'); await expect(page.getByText('No attendance analytics match these filters.').first()).toBeVisible()
  await page.unroute('**/api/v1/dashboard/**'); await page.route('**/api/v1/dashboard/**', async (route) => respond(route, 'unavailable')); await page.getByRole('button', { name: 'Refresh' }).click()
  await expect(page.getByText('Attendance analytics are temporarily unavailable.').first()).toBeVisible()
  await page.unroute('**/api/v1/dashboard/**'); await page.route('**/api/v1/dashboard/**', async (route) => { const url = new URL(route.request().url()); if (url.pathname.endsWith('/work-hours/ranking') && url.searchParams.get('department_id') === departmentByName.get('Training')) await new Promise((resolve) => setTimeout(resolve, 300)); return respond(route, 'available') }); await page.getByRole('button', { name: 'Refresh' }).click(); await expect(page.getByLabel('Department').locator('option')).toHaveCount(6)
  await page.getByLabel('Department').selectOption(departmentByName.get('Training')!); await page.getByRole('button', { name: 'Apply filters' }).click(); await page.getByLabel('Department').selectOption(departmentByName.get('Operations')!); await page.getByRole('button', { name: 'Apply filters' }).click()
  await expect(page.getByTestId('employee-chart-name').first()).toBeVisible()
})

test('invalid date ranges are localized and issue no dashboard requests in English and Arabic', async ({ page }) => {
  await mockApp(page); const requests: URL[] = []
  page.on('request', (request) => { if (request.url().includes('/api/v1/dashboard/')) requests.push(new URL(request.url())) })
  await page.goto('/dashboard'); await expect(page.getByTestId('kpi-employees')).toBeVisible(); requests.length = 0
  await page.getByLabel('Start date').fill('2026-07-20'); await page.getByLabel('End date').fill('2026-07-10'); await page.getByRole('button', { name: 'Apply filters' }).click()
  await expect(page.getByText('Start date must be on or before end date.')).toBeVisible(); expect(requests).toHaveLength(0)
  await expect(page.getByLabel('Start date')).toHaveAttribute('max', '2026-07-10'); await expect(page.getByLabel('End date')).toHaveAttribute('min', '2026-07-20')
  await page.getByTestId('dashboard-reset').click(); await expect(page.locator('#dashboard-filter-error')).toHaveCount(0)
  await page.evaluate(() => localStorage.setItem('lang', 'ar')); await page.reload(); await expect(page.locator('html')).toHaveAttribute('dir', 'rtl'); await expect(page.getByTestId('employee-chart-name')).toHaveCount(12); requests.length = 0
  await page.getByTestId('dashboard-start').fill('2026-07-20'); await page.getByTestId('dashboard-end').fill('2026-07-10'); await page.getByTestId('dashboard-apply').click()
  await expect(page.getByText('يجب أن يكون تاريخ البدء في تاريخ الانتهاء أو قبله.')).toBeVisible(); expect(requests).toHaveLength(0)
})

test('department refresh preserves the selected fallback and ALL omits department_id', async ({ page }) => {
  await mockApp(page); await page.unroute('**/api/v1/dashboard/**')
  let departmentCalls = 0; const analyticsRequests: URL[] = []
  await page.route('**/api/v1/dashboard/**', async (route) => {
    const url = new URL(route.request().url())
    if (url.pathname.endsWith('/departments')) {
      departmentCalls += 1
      if (departmentCalls === 1) return route.fulfill({ json: { success: true, data: [{ department_id: 1, department_name: 'Operations' }, { department_id: 2, department_name: 'Support' }] } })
      if (departmentCalls === 2) return route.fulfill({ status: 503, json: { detail: 'Attendance analytics are temporarily unavailable' } })
      return route.fulfill({ json: { success: true, data: [{ department_id: 2, department_name: 'Support' }] } })
    }
    analyticsRequests.push(url); return respond(route, 'available')
  })
  await page.goto('/dashboard'); const select = page.getByTestId('dashboard-department')
  await expect(select.locator('option')).toHaveText(['ALL', 'Operations', 'Support'])
  await select.selectOption('1'); await page.getByRole('button', { name: 'Apply filters' }).click()
  await expect.poll(() => analyticsRequests.filter((url) => url.searchParams.get('department_id') === '1').length).toBe(4)
  await page.getByRole('button', { name: 'Refresh' }).click()
  await expect(page.getByText('Department options are unavailable; the current selection is preserved.')).toBeVisible()
  await expect(select).toHaveValue('1'); await expect(select.locator('option')).toHaveText(['ALL', '1'])
  await page.getByRole('button', { name: 'Refresh' }).click(); await expect(select).toHaveValue('1')
  analyticsRequests.length = 0; await select.selectOption(''); await page.getByRole('button', { name: 'Apply filters' }).click()
  await expect.poll(() => analyticsRequests.length).toBe(4); expect(analyticsRequests.every((url) => !url.searchParams.has('department_id'))).toBeTruthy()
})

test('effective range is hidden while replacement overview loads and after it fails', async ({ page }) => {
  await mockApp(page); await page.goto('/dashboard'); await expect(page.getByText(/Effective range:/)).toBeVisible()
  await page.unroute('**/api/v1/dashboard/**'); await page.route('**/api/v1/dashboard/**', async (route) => {
    if (new URL(route.request().url()).pathname.endsWith('/overview')) { await new Promise((resolve) => setTimeout(resolve, 300)); return respond(route, 'unavailable') }
    return respond(route, 'available')
  })
  await page.getByLabel('Department').selectOption(departmentByName.get('Research')!); await page.getByRole('button', { name: 'Apply filters' }).click()
  await expect(page.getByText(/Effective range:/)).toHaveCount(0); await expect(page.getByText('Attendance analytics are temporarily unavailable.')).toBeVisible(); await expect(page.getByText(/Effective range:/)).toHaveCount(0)
})

test('renders four accented primary KPIs separately from six secondary KPIs in LTR and RTL', async ({ page }) => {
  await mockApp(page); await page.goto('/dashboard')
  const primary = page.getByTestId('kpi-primary-grid'); const secondary = page.getByTestId('kpi-secondary-grid')
  await expect(primary.locator('[data-kpi-tier="primary"]')).toHaveCount(4); await expect(secondary.locator('[data-kpi-tier="secondary"]')).toHaveCount(6)
  await expect(primary.getByTestId('kpi-exceptions')).toBeVisible(); await expect(secondary.getByTestId('kpi-scheduled')).toBeVisible()
  expect(await primary.locator('article').evaluateAll((cards) => cards.every((card) => getComputedStyle(card).borderInlineStartWidth === '4px'))).toBeTruthy()
  expect(await secondary.locator('article').evaluateAll((cards) => cards.every((card) => getComputedStyle(card).borderInlineStartWidth !== '4px'))).toBeTruthy()
  await page.evaluate(() => localStorage.setItem('lang', 'ar')); await page.reload(); await expect(page.locator('html')).toHaveAttribute('dir', 'rtl')
  const employeeStyle = await page.getByTestId('kpi-employees').evaluate((card) => { const style = getComputedStyle(card); return { inlineStart: style.borderInlineStartWidth, right: style.borderRightWidth } })
  expect(employeeStyle).toEqual({ inlineStart: '4px', right: '4px' })
})

test('an older delayed response cannot overwrite newer dashboard state', async ({ page }) => {
  await mockApp(page); await page.unroute('**/api/v1/dashboard/**')
  await page.route('**/api/v1/dashboard/**', async (route) => {
    const url = new URL(route.request().url())
    if (url.pathname.endsWith('/overview')) {
      const department = url.searchParams.get('department_id'); if (department === departmentByName.get('Training')) await new Promise((resolve) => setTimeout(resolve, 350))
      return route.fulfill({ json: { success: true, data: { ...overview, employee_count: department === departmentByName.get('Operations') ? 99 : department === departmentByName.get('Training') ? 1 : 7 } } })
    }
    return respond(route, 'available')
  })
  await page.goto('/dashboard'); await expect(page.getByTestId('kpi-employees')).toContainText('7')
  await page.getByLabel('Department').selectOption(departmentByName.get('Training')!); await page.getByRole('button', { name: 'Apply filters' }).click()
  await page.getByLabel('Department').selectOption(departmentByName.get('Operations')!); await page.getByRole('button', { name: 'Apply filters' }).click()
  await expect(page.getByTestId('kpi-employees')).toContainText('99'); await page.waitForTimeout(450); await expect(page.getByTestId('kpi-employees')).toContainText('99')
})

test.describe('PostgreSQL calendar and wall-clock values', () => {
  test.use({ timezoneId: 'America/Los_Angeles' })
  test('do not shift in a browser timezone west of UTC', async ({ page }) => {
    await mockApp(page); await page.goto('/dashboard')
    await expect(page.getByRole('cell', { name: 'Jul 30, 2026' }).first()).toBeVisible(); await expect(page.getByRole('cell', { name: '08:10 AM' }).first()).toBeVisible()
  })
})
