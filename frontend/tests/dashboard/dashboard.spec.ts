import { expect, test, type Page, type Route } from '@playwright/test'

const duration = { scheduled_seconds: 32_400, actual_seconds: 30_600, normal_seconds: 28_800, overtime_seconds: 1_800, late_seconds: 300, early_seconds: 0, absent_seconds: 0 }
const range = { effective_start_date: '2026-07-01', effective_end_date: '2026-07-30', source_latest_report_date: '2026-07-30', org_id: null, data_status: 'available', duration_unit: 'seconds' }
const overview = { ...range, ...duration, report_row_count: 22, report_day_count: 20, employee_count: 7, reported_exception_count: 2 }
const point = { ...duration, period_key: '2026-W30', period_start: '2026-07-20', period_end: '2026-07-26', report_row_count: 10, employee_count: 7 }
const rankingItem = { ...duration, rank: 1, org_id: 'ORG-1', employee_key: 'ORG-1:E-01', person_id: 'P-01', person_no: 'E-01', person_name: 'Amina Noor', department_name: 'Operations', report_day_count: 20 }
const missingRankingItem = { ...rankingItem, rank: 2, org_id: 'ORG-2', employee_key: 'SHARED:E-02', person_id: null, person_no: 'E-02', person_name: null, department_name: 'International Operations and Workforce Planning Department' }
const exception = { id: 1, org_id: 'ORG-1', person_id: 'P-01', person_no: 'E-01', person_name: 'Amina Noor', report_date: '2026-07-30', clock_time: '2026-07-30T08:10:00', device_key: 'D-01', device_name: 'Main Gate' }
const missingException = { ...exception, id: 2, org_id: 'ORG-2', person_id: null, person_no: null, person_name: null, device_name: null }

type Mode = 'available' | 'empty' | 'partial' | 'unavailable'

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
  if (mode === 'unavailable') return route.fulfill({ status: 503, json: { error: { code: 'DASHBOARD_UNAVAILABLE', message: 'private detail must not render' } } })
  if (mode === 'partial' && path.endsWith('/work-hours/trend')) return route.fulfill({ status: 503, json: { error: { code: 'DASHBOARD_UNAVAILABLE' } } })
  const empty = mode === 'empty'
  if (path.endsWith('/overview')) return route.fulfill({ json: { success: true, data: empty ? { ...overview, data_status: 'empty', report_row_count: 0, report_day_count: 0, employee_count: 0, reported_exception_count: 0 } : overview } })
  if (path.endsWith('/work-hours/trend')) return route.fulfill({ json: { success: true, data: { ...range, granularity: url.searchParams.get('granularity') ?? 'week', points: empty ? [] : [point] } } })
  if (path.endsWith('/work-hours/ranking')) return route.fulfill({ json: { success: true, data: { ...range, org_id: url.searchParams.get('org_id'), items: empty ? [] : [rankingItem, missingRankingItem] } } })
  return route.fulfill({ json: { success: true, data: empty ? [] : [exception, missingException], meta: { page: Number(url.searchParams.get('page') ?? 1), page_size: Number(url.searchParams.get('page_size') ?? 20), total: empty ? 0 : 41, pages: empty ? 0 : 3 } } })
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
  await expect.poll(() => dashboardRequests.length).toBe(4)
  expect(dashboardRequests.every((url) => !url.searchParams.has('start_date') && !url.searchParams.has('end_date'))).toBeTruthy()
})

test('keeps draft filters local, applies organization scope, and isolates section controls', async ({ page }) => {
  await mockApp(page)
  const requests: URL[] = []; page.on('request', (request) => { if (request.url().includes('/api/v1/dashboard/')) requests.push(new URL(request.url())) })
  await page.goto('/dashboard'); await expect(page.getByText('Amina Noor').first()).toBeVisible(); requests.length = 0
  await page.getByLabel('Start date').fill('2026-07-10'); await page.getByLabel('End date').fill('2026-07-20'); await page.getByLabel('Organization').fill('ORG-2'); await page.waitForTimeout(100)
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
  await expect(page.getByText('private detail must not render')).toHaveCount(0)
})

test('supports Arabic RTL, dark theme, and a mobile viewport', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 }); await mockApp(page)
  await page.addInitScript(() => { localStorage.setItem('lang', 'ar'); localStorage.setItem('theme', 'dark') })
  await page.goto('/dashboard'); await expect(page.getByTestId('attendance-dashboard')).toBeVisible()
  await expect(page.locator('html')).toHaveAttribute('dir', 'rtl'); await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark')
  await expect(page.locator('body')).not.toHaveCSS('overflow-x', 'scroll')
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
  await page.getByLabel('Organization').fill('SLOW'); await page.getByRole('button', { name: 'Apply filters' }).click()
  await page.getByLabel('Organization').fill('FAST'); await page.getByRole('button', { name: 'Apply filters' }).click()
  await expect(page.getByTestId('kpi-employees')).toContainText('99'); await page.waitForTimeout(450)
  await expect(page.getByTestId('kpi-employees')).toContainText('99')
  await expect(page.getByText(/reason|clock_photo_id/i)).toHaveCount(0)
})
