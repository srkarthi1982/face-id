import { expect, test, type Page, type Route } from '@playwright/test'

type PermissionMode = 'read' | 'write'

const departments = [
  { id: 1, name: 'Operations', code: 'OPS', description: null, parent_id: null, path: '/Operations', is_active: true, sort_order: 0, created_at: '2026-01-01T00:00:00Z', updated_at: '2026-01-01T00:00:00Z' },
]

const timing = {
  id: 10,
  department_id: 1,
  department_name: 'Operations',
  start_day: 'monday',
  end_day: 'friday',
  start_time: '08:00:00',
  end_time: '16:00:00',
  is_active: true,
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
}

async function mockTimingPage(page: Page, mode: PermissionMode = 'write') {
  const calls: { method: string; path: string; body?: unknown }[] = []
  await page.addInitScript(() => {
    localStorage.setItem('access_token', 'timing-test-token')
    localStorage.setItem('lang', 'en')
    localStorage.setItem('theme', 'light')
  })
  await page.route('**/api/v1/auth/me**', async (route) => {
    const url = new URL(route.request().url())
    if (url.pathname.endsWith('/permissions')) {
      return route.fulfill({ json: { success: true, data: mode === 'write' ? ['timing:read', 'timing:write'] : ['timing:read'] } })
    }
    return route.fulfill({ json: { success: true, data: { id: 1, email: 'timing@example.test', username: 'timing', roles: ['viewer'], auth_provider: 'local', created_at: '2026-01-01T00:00:00Z', updated_at: '2026-01-01T00:00:00Z', version: 1 } } })
  })
  await page.route('**/api/v1/master-data/**', async (route: Route) => {
    const request = route.request()
    const url = new URL(request.url())
    calls.push({ method: request.method(), path: url.pathname, body: request.postDataJSON?.() })
    if (url.pathname.endsWith('/departments') || url.pathname.endsWith('/departments?active_only=true')) return route.fulfill({ json: departments })
    if (url.pathname.endsWith('/timings') && request.method() === 'GET') return route.fulfill({ json: [timing] })
    if (url.pathname.endsWith('/timings') && request.method() === 'POST') return route.fulfill({ status: 201, json: { ...timing, id: 11, ...(request.postDataJSON() as object) } })
    if (url.pathname.endsWith('/timings/10') && request.method() === 'PUT') return route.fulfill({ json: { ...timing, ...(request.postDataJSON() as object) } })
    if (url.pathname.endsWith('/timings/10') && request.method() === 'DELETE') return route.fulfill({ status: 204, body: '' })
    return route.fulfill({ status: 404, json: { detail: 'not found' } })
  })
  return calls
}

test('read-only Timing users can view schedules without write controls', async ({ page }) => {
  const calls = await mockTimingPage(page, 'read')
  await page.goto('/master/timings')
  await expect(page.getByRole('heading', { name: 'Timings' })).toBeVisible()
  await expect(page.getByText('Operations')).toBeVisible()
  await expect(page.getByRole('button', { name: 'Add' })).toHaveCount(0)
  await expect(page.getByRole('button', { name: 'Edit' })).toHaveCount(0)
  await expect(page.getByRole('button', { name: 'Delete' })).toHaveCount(0)
  expect(calls.every((call) => call.method === 'GET')).toBeTruthy()
})

test('Timing write users can create, validate, edit, and delete timings', async ({ page }) => {
  const calls = await mockTimingPage(page, 'write')
  await page.goto('/master/timings')
  await page.getByRole('button', { name: 'Add' }).click()
  await page.getByLabel('Start Time').fill('20:00')
  await page.getByLabel('End Time').fill('06:00')
  await page.getByRole('button', { name: 'Save' }).click()
  await expect(page.getByRole('alert')).toContainText('Start time must be before end time')

  await page.getByLabel('Start Time').fill('08:00')
  await page.getByLabel('End Time').fill('16:00')
  await page.getByRole('button', { name: 'Save' }).click()
  await expect.poll(() => calls.some((call) => call.method === 'POST' && call.path.endsWith('/timings'))).toBeTruthy()

  await page.getByRole('button', { name: 'Edit' }).click()
  await page.getByLabel('Start Time').fill('07:30')
  await page.getByRole('button', { name: 'Save' }).click()
  await expect.poll(() => calls.some((call) => call.method === 'PUT' && call.path.endsWith('/timings/10'))).toBeTruthy()

  await page.getByRole('button', { name: 'Delete' }).click()
  await expect(page.getByText('Delete this timing?')).toBeVisible()
  await page.getByRole('button', { name: 'Delete' }).last().click()
  await expect.poll(() => calls.some((call) => call.method === 'DELETE' && call.path.endsWith('/timings/10'))).toBeTruthy()
})
