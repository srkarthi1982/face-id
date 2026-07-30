import { expect, test, type Page, type Route } from '@playwright/test'

const duration = { scheduled_seconds: 32_400, actual_seconds: 30_600, normal_seconds: 28_800, overtime_seconds: 1_800, late_seconds: 300, early_seconds: 0, absent_seconds: 0 }
const range = { effective_start_date: '2026-07-01', effective_end_date: '2026-07-30', source_latest_report_date: '2026-07-30', org_id: null, data_status: 'available', duration_unit: 'seconds' }
const overview = { ...range, ...duration, report_row_count: 22, report_day_count: 20, employee_count: 7, reported_exception_count: 3 }
const point = { ...duration, period_key: '2026-W30', period_start: '2026-07-20', period_end: '2026-07-26', report_row_count: 10, employee_count: 7 }
const rankingItem = { ...duration, rank: 1, org_id: 'ORG-1', employee_key: 'ORG-1:E-01', person_id: 'P-01', person_no: 'E-01', person_name: 'Amina Noor', department_name: 'Operations', report_day_count: 20 }
const missingRankingItem = { ...rankingItem, rank: 2, org_id: 'ORG-2', employee_key: 'SHARED:E-02', person_id: null, person_no: 'E-02', person_name: null, department_name: 'International Operations and Workforce Planning Department' }
const exception = { id: 1, org_id: 'ORG-1', person_id: 'P-01', person_no: 'E-01', person_name: 'Amina Noor', report_date: '2026-07-30', clock_time: '2026-07-30T08:10:00', device_key: 'D-01', device_name: 'Main Gate' }
const missingException = { ...exception, id: 2, org_id: 'ORG-2', person_id: null, person_no: null, person_name: null, device_name: null }
const recentException = { ...exception, id: 3, org_id: 'ORG-2', person_id: 'P-03', person_no: 'E-03', person_name: 'Omar Saleh', report_date: '2026-07-29', clock_time: '2026-07-29T16:18:00' }
const organizations = ['FAST', 'ORG-1', 'ORG-2', 'ORG-NEW', 'SLOW', 'UNSAVED-ORG'].map((org_id) => ({ org_id }))

type Mode = 'available' | 'empty' | 'partial' | 'unavailable' | 'invalid'

async function mockApp(page: Page, mode: Mode = 'available') {
  await page.addInitScript(() => {
    localStorage.setItem('access_token', 'dashboard-test-token')
    if (!localStorage.getItem('lang')) localStorage.setItem('lang', 'en')
    if (!localStorage.getItem('theme')) localStorage.setItem('theme', 'light')
  })
  await page.route('**/api/v1/auth/me**', async (route) => {
    if (new URL(route.request().url()).pathname.endsWith('/permissions')) return route.fulfill({ json: { success: true, data: ['analytics:read'] } })
    return route.fulfill({ json: { success: true, data: { id: 1, email: 'dashboard@example.test', username: 'dashboard', full_name: 'Dashboard User', roles: ['viewer'], auth_provider: 'local', created_at: '2026-01-01T00:00:00Z', updated_at: '2026-01-01T00:00:00Z', version: 1, created_by_id: null, updated_by_id: null } } })
  })
  await page.route('**/api/v1/dashboard/**', async (route) => respond(route, mode))
}

async function respond(route: Route, mode: Mode) {
  const url = new URL(route.request().url()); const path = url.pathname
  if (mode === 'unavailable') return route.fulfill({ status: 503, json: { detail: 'Attendance analytics are temporarily unavailable' } })
  if (mode === 'invalid') return route.fulfill({ status: 422, json: { detail: [{ loc: ['query', 'start_date'], msg: 'Invalid range', type: 'value_error' }] } })
  if (mode === 'partial' && path.endsWith('/work-hours/trend')) return route.fulfill({ status: 503, json: { detail: 'Attendance analytics are temporarily unavailable' } })
  const empty = mode === 'empty'
  if (path.endsWith('/organizations')) return route.fulfill({ json: { success: true, data: organizations } })
  if (path.endsWith('/overview')) return route.fulfill({ json: { success: true, data: empty ? { ...overview, data_status: 'empty', report_row_count: 0, report_day_count: 0, employee_count: 0, reported_exception_count: 0 } : overview } })
  if (path.endsWith('/work-hours/trend')) return route.fulfill({ json: { success: true, data: { ...range, granularity: url.searchParams.get('granularity') ?? 'week', points: empty ? [] : [point] } } })
  if (path.endsWith('/work-hours/ranking')) return route.fulfill({ json: { success: true, data: { ...range, org_id: url.searchParams.get('org_id'), items: empty ? [] : [rankingItem, missingRankingItem] } } })
  return route.fulfill({ json: { success: true, data: empty ? [] : [exception, missingException, recentException], meta: { page: Number(url.searchParams.get('page') ?? 1), page_size: Number(url.searchParams.get('page_size') ?? 20), total: empty ? 0 : 41, pages: empty ? 0 : 3 } } })
}

test('loads all analytics, formats durations, and omits empty date filters', async ({ page }) => {
  const dashboardRequests: URL[] = []
  await mockApp(page)
  page.on('request', (request) => { if (request.url().includes('/api/v1/dashboard/')) dashboardRequests.push(new URL(request.url())) })
  await page.goto('/dashboard')
  await expect(page.getByTestId('attendance-dashboard')).toBeVisible()
  await expect(page.getByText('8 h 30 min').first()).toBeVisible()
  await expect(page.getByRole('cell', { name: 'Amina Noor' }).first()).toBeVisible()
  await expect(page.getByRole('cell', { name: 'E-02' }).first()).toBeVisible()
  await expect(page.getByRole('cell', { name: 'ORG-1' }).first()).toBeVisible(); await expect(page.getByRole('cell', { name: 'ORG-2' }).first()).toBeVisible()
  await expect(page.getByText('Employee unavailable')).toBeVisible()
  await expect(page.getByTestId('dashboard-org')).toHaveJSProperty('tagName', 'SELECT')
  await expect(page.getByTestId('dashboard-org').locator('option').first()).toHaveText('ALL'); await expect(page.getByTestId('dashboard-org')).toHaveValue('')
  await expect(page.getByTestId('dashboard-org').locator('option')).toHaveText(['ALL', ...organizations.map((option) => option.org_id)])
  await expect(page.getByRole('cell', { name: 'Omar Saleh' })).toBeVisible()
  await expect.poll(() => dashboardRequests.length).toBe(5)
  expect(dashboardRequests.every((url) => !url.searchParams.has('start_date') && !url.searchParams.has('end_date'))).toBeTruthy()
})

test('keeps draft filters local, applies organization scope, and isolates section controls', async ({ page }) => {
  await mockApp(page)
  const requests: URL[] = []; page.on('request', (request) => { if (request.url().includes('/api/v1/dashboard/')) requests.push(new URL(request.url())) })
  await page.goto('/dashboard'); await expect(page.getByText('Amina Noor').first()).toBeVisible(); requests.length = 0
  await page.getByLabel('Start date').fill('2026-07-10'); await page.getByLabel('End date').fill('2026-07-20'); await page.getByLabel('Organization').selectOption('ORG-2'); await page.waitForTimeout(100)
  expect(requests).toHaveLength(0)
  await page.getByRole('button', { name: 'Apply filters' }).click(); await expect.poll(() => requests.length).toBe(4)
  expect(requests.every((url) => url.searchParams.get('org_id') === 'ORG-2' && url.searchParams.get('start_date') === '2026-07-10' && url.searchParams.get('end_date') === '2026-07-20')).toBeTruthy()
  requests.length = 0; await page.getByLabel('Trend granularity').selectOption('month'); await expect.poll(() => requests.length).toBe(1)
  expect(requests[0].pathname).toContain('work-hours/trend'); expect(requests[0].searchParams.get('granularity')).toBe('month')
  requests.length = 0; await page.getByRole('button', { name: 'Next' }).click(); await expect.poll(() => requests.length).toBe(1)
  expect(requests[0].pathname).toContain('attendance-exceptions'); expect(requests[0].searchParams.get('page')).toBe('2')
  requests.length = 0; await page.getByRole('button', { name: 'Reset' }).click(); await expect(page.getByLabel('Organization')).toHaveValue(''); await expect.poll(() => requests.length).toBe(4)
  expect(requests.every((url) => !url.searchParams.has('start_date') && !url.searchParams.has('end_date') && !url.searchParams.has('org_id'))).toBeTruthy()
})

test('renders independent empty, unavailable, and partial-failure states without leaking details', async ({ page }) => {
  await mockApp(page, 'partial'); await page.goto('/dashboard')
  await expect(page.getByText('Amina Noor').first()).toBeVisible()
  await expect(page.getByText('Attendance analytics are temporarily unavailable.')).toBeVisible()
  await page.unroute('**/api/v1/dashboard/**'); await page.route('**/api/v1/dashboard/**', async (route) => respond(route, 'empty'))
  await page.getByRole('button', { name: 'Refresh' }).click()
  await expect(page.getByText('No attendance analytics match these filters.').first()).toBeVisible()
  await page.unroute('**/api/v1/dashboard/**'); await page.route('**/api/v1/dashboard/**', async (route) => respond(route, 'unavailable'))
  await page.getByRole('button', { name: 'Refresh' }).click()
  await expect(page.getByText('Attendance analytics are temporarily unavailable.').first()).toBeVisible()
  await expect(page.getByText('Attendance analytics are temporarily unavailable', { exact: true })).toHaveCount(0)
  await page.unroute('**/api/v1/dashboard/**'); await page.route('**/api/v1/dashboard/**', async (route) => respond(route, 'invalid'))
  await page.getByRole('button', { name: 'Refresh' }).click()
  await expect(page.getByText('This dashboard section could not be loaded.').first()).toBeVisible()
  await expect(page.getByText('Invalid range')).toHaveCount(0)
})

test('supports Arabic RTL, dark theme, and a mobile viewport', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 }); await mockApp(page)
  await page.addInitScript(() => { localStorage.setItem('lang', 'ar'); localStorage.setItem('theme', 'dark') })
  await page.goto('/dashboard'); await expect(page.getByTestId('attendance-dashboard')).toBeVisible()
  await expect(page.locator('html')).toHaveAttribute('dir', 'rtl'); await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark')
  await expect(page.getByTestId('dashboard-org').locator('option').first()).toHaveText('الكل')
  await expect(page.locator('body')).not.toHaveCSS('overflow-x', 'scroll')
})

test('section controls do not interrupt unrelated slow requests or leave loading panels', async ({ page }) => {
  await mockApp(page); await page.unroute('**/api/v1/dashboard/**')
  const requests: URL[] = []
  await page.route('**/api/v1/dashboard/**', async (route) => {
    const url = new URL(route.request().url()); requests.push(url)
    if (url.pathname.endsWith('/overview') || url.pathname.endsWith('/work-hours/ranking')) await new Promise((resolve) => setTimeout(resolve, 450))
    return respond(route, 'available')
  })
  await page.goto('/dashboard')
  await page.getByLabel('Trend granularity').selectOption('month'); await page.getByRole('button', { name: 'Next' }).click()
  await page.getByLabel('Trend granularity').selectOption('day'); await page.getByLabel('Trend granularity').selectOption('week')
  await expect(page.getByTestId('kpi-employees')).toContainText('7'); await expect(page.getByText('Amina Noor').first()).toBeVisible()
  await expect(page.getByRole('status')).toHaveCount(0)
  expect(requests.filter((url) => url.pathname.endsWith('/overview'))).toHaveLength(1)
  expect(requests.filter((url) => url.pathname.endsWith('/work-hours/ranking'))).toHaveLength(1)
  expect(requests.filter((url) => url.pathname.endsWith('/work-hours/trend')).length).toBeGreaterThan(1)
  expect(requests.filter((url) => url.pathname.endsWith('/attendance-exceptions')).length).toBeGreaterThan(1)
})

test('ranking limit reloads ranking only and preserves applied filters', async ({ page }) => {
  await mockApp(page); const requests: URL[] = []
  page.on('request', (request) => { if (request.url().includes('/api/v1/dashboard/')) requests.push(new URL(request.url())) })
  await page.goto('/dashboard'); await expect(page.getByText('Amina Noor').first()).toBeVisible(); requests.length = 0
  await page.getByLabel('Organization').selectOption('UNSAVED-ORG'); await page.getByLabel('Rows', { exact: true }).selectOption('20')
  await expect.poll(() => requests.length).toBe(1)
  expect(requests[0].pathname).toContain('/work-hours/ranking'); expect(requests[0].searchParams.get('limit')).toBe('20'); expect(requests[0].searchParams.has('org_id')).toBeFalsy()
  await expect(page.getByLabel('Organization')).toHaveValue('UNSAVED-ORG'); await expect(page.getByLabel('Rows', { exact: true })).toHaveValue('20')
  const header = page.getByTestId('ranking-header'); await expect(header.getByRole('heading')).toBeVisible(); await expect(header.getByLabel('Rows', { exact: true })).toBeVisible()
  const titleBox = await header.getByRole('heading').boundingBox(); const rowsBox = await header.getByLabel('Rows', { exact: true }).boundingBox()
  expect(titleBox && rowsBox && Math.abs(titleBox.y - rowsBox.y) < 16).toBeTruthy()
})

test('organization refresh preserves a truthful selected fallback and ALL omits org_id', async ({ page }) => {
  await mockApp(page); await page.unroute('**/api/v1/dashboard/**')
  let organizationCalls = 0
  const analyticsRequests: URL[] = []
  await page.route('**/api/v1/dashboard/**', async (route) => {
    const url = new URL(route.request().url())
    if (url.pathname.endsWith('/organizations')) {
      organizationCalls += 1
      if (organizationCalls === 1) return route.fulfill({ json: { success: true, data: [{ org_id: 'ORG-1' }, { org_id: 'ORG-2' }] } })
      if (organizationCalls === 2) return route.fulfill({ status: 503, json: { detail: 'Attendance analytics are temporarily unavailable' } })
      return route.fulfill({ json: { success: true, data: [{ org_id: 'ORG-2' }] } })
    }
    analyticsRequests.push(url)
    return respond(route, 'available')
  })
  await page.goto('/dashboard'); const select = page.getByTestId('dashboard-org')
  await expect(select.locator('option')).toHaveText(['ALL', 'ORG-1', 'ORG-2'])
  await select.selectOption('ORG-1'); await page.getByRole('button', { name: 'Apply filters' }).click()
  await expect.poll(() => analyticsRequests.filter((url) => url.searchParams.get('org_id') === 'ORG-1').length).toBe(4)
  await page.getByRole('button', { name: 'Refresh' }).click()
  await expect(page.getByText('Organization options are unavailable; the current selection is preserved.')).toBeVisible()
  await expect(select).toHaveValue('ORG-1'); await expect(select.locator('option')).toHaveText(['ALL', 'ORG-1'])
  analyticsRequests.length = 0; await page.getByRole('button', { name: 'Apply filters' }).click()
  await expect.poll(() => analyticsRequests.length).toBe(4); expect(analyticsRequests.every((url) => url.searchParams.get('org_id') === 'ORG-1')).toBeTruthy()
  await page.getByRole('button', { name: 'Refresh' }).click()
  await expect(select).toHaveValue('ORG-1'); await expect(select.locator('option')).toHaveText(['ALL', 'ORG-1', 'ORG-2'])
  analyticsRequests.length = 0; await select.selectOption(''); await page.getByRole('button', { name: 'Apply filters' }).click()
  await expect.poll(() => analyticsRequests.length).toBe(4); expect(analyticsRequests.every((url) => !url.searchParams.has('org_id'))).toBeTruthy()
})

test('invalid date ranges are localized and issue no dashboard requests', async ({ page }) => {
  await mockApp(page); const requests: URL[] = []
  page.on('request', (request) => { if (request.url().includes('/api/v1/dashboard/')) requests.push(new URL(request.url())) })
  await page.goto('/dashboard'); await expect(page.getByTestId('kpi-employees')).toBeVisible(); requests.length = 0
  await page.getByLabel('Start date').fill('2026-07-20'); await page.getByLabel('End date').fill('2026-07-10'); await page.getByRole('button', { name: 'Apply filters' }).click()
  await expect(page.getByText('Start date must be on or before end date.')).toBeVisible(); expect(requests).toHaveLength(0)
  await expect(page.getByLabel('Start date')).toHaveAttribute('max', '2026-07-10'); await expect(page.getByLabel('End date')).toHaveAttribute('min', '2026-07-20')
  await page.getByTestId('dashboard-reset').click(); await expect(page.locator('#dashboard-filter-error')).toHaveCount(0)
  await page.evaluate(() => localStorage.setItem('lang', 'ar')); await page.reload(); await expect(page.getByTestId('attendance-dashboard')).toBeVisible(); requests.length = 0
  await page.getByTestId('dashboard-start').fill('2026-07-20'); await page.getByTestId('dashboard-end').fill('2026-07-10'); await page.getByTestId('dashboard-apply').click()
  await expect(page.getByText('يجب أن يكون تاريخ البدء في تاريخ الانتهاء أو قبله.')).toBeVisible(); expect(requests).toHaveLength(0)
})

test('effective range is hidden while replacement overview loads and after it fails', async ({ page }) => {
  await mockApp(page); await page.goto('/dashboard'); await expect(page.getByText(/Effective range:/)).toBeVisible()
  await page.unroute('**/api/v1/dashboard/**'); await page.route('**/api/v1/dashboard/**', async (route) => {
    if (new URL(route.request().url()).pathname.endsWith('/overview')) { await new Promise((resolve) => setTimeout(resolve, 300)); return respond(route, 'unavailable') }
    return respond(route, 'available')
  })
  await page.getByLabel('Organization').selectOption('ORG-NEW'); await page.getByRole('button', { name: 'Apply filters' }).click()
  await expect(page.getByText(/Effective range:/)).toHaveCount(0); await expect(page.getByText('Attendance analytics are temporarily unavailable.')).toBeVisible(); await expect(page.getByText(/Effective range:/)).toHaveCount(0)
})

test('chart uses live theme variables and exposes the complete accessible summary', async ({ page }) => {
  await mockApp(page); await page.goto('/dashboard'); const scheduled = page.locator('path[data-series="scheduled"]')
  await expect(scheduled).toHaveAttribute('stroke', 'var(--text-muted)')
  const before = await scheduled.evaluate((element) => getComputedStyle(element).stroke)
  await page.evaluate(() => document.documentElement.setAttribute('data-theme', 'dark'))
  const after = await scheduled.evaluate((element) => getComputedStyle(element).stroke); expect(after).not.toBe(before)
  for (const header of ['Period', 'Scheduled work', 'Actual work', 'Overtime', 'Employees']) await expect(page.getByRole('columnheader', { name: header }).last()).toBeAttached()
})

test('supports the language, theme, viewport, and keyboard acceptance matrix', async ({ page }) => {
  await mockApp(page); await page.goto('/dashboard')
  for (const viewport of [{ width: 360, height: 800 }, { width: 768, height: 900 }, { width: 1440, height: 1000 }]) {
    await page.setViewportSize(viewport)
    for (const lang of ['en', 'ar']) for (const theme of ['light', 'dark']) {
      await page.evaluate(({ lang, theme }) => { localStorage.setItem('lang', lang); localStorage.setItem('theme', theme) }, { lang, theme })
      await page.reload(); await expect(page.getByTestId('attendance-dashboard')).toBeVisible()
      await expect(page.locator('html')).toHaveAttribute('dir', lang === 'ar' ? 'rtl' : 'ltr'); await expect(page.locator('html')).toHaveAttribute('data-theme', theme)
      expect(await page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth)).toBeTruthy()
    }
  }
  await page.getByTestId('dashboard-org').focus(); await page.keyboard.press('Tab'); await expect(page.getByTestId('dashboard-apply')).toBeFocused()
})

test('a delayed older filter response cannot overwrite newer dashboard state', async ({ page }) => {
  await mockApp(page)
  await page.unroute('**/api/v1/dashboard/**')
  await page.route('**/api/v1/dashboard/**', async (route) => {
    const url = new URL(route.request().url())
    if (url.pathname.endsWith('/overview')) {
      const org = url.searchParams.get('org_id')
      if (org === 'SLOW') await new Promise((resolve) => setTimeout(resolve, 350))
      return route.fulfill({ json: { success: true, data: { ...overview, employee_count: org === 'FAST' ? 99 : org === 'SLOW' ? 1 : 7 } } })
    }
    return respond(route, 'available')
  })
  await page.goto('/dashboard'); await expect(page.getByTestId('kpi-employees')).toContainText('7')
  await page.getByLabel('Organization').selectOption('SLOW'); await page.getByRole('button', { name: 'Apply filters' }).click()
  await page.getByLabel('Organization').selectOption('FAST'); await page.getByRole('button', { name: 'Apply filters' }).click()
  await expect(page.getByTestId('kpi-employees')).toContainText('99'); await page.waitForTimeout(450)
  await expect(page.getByTestId('kpi-employees')).toContainText('99')
  await expect(page.getByText(/reason|clock_photo_id/i)).toHaveCount(0)
})

test.describe('Luna calendar and wall-clock values', () => {
  test.use({ timezoneId: 'America/Los_Angeles' })
  test('do not shift in a browser timezone west of UTC', async ({ page }) => {
    await mockApp(page); await page.goto('/dashboard')
    await expect(page.getByRole('cell', { name: 'Jul 30, 2026' }).first()).toBeVisible()
    await expect(page.getByRole('cell', { name: '08:10 AM' }).first()).toBeVisible()
  })
})
