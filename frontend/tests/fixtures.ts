import { test as base, expect } from '@playwright/test'
export const test = base
export { expect }

const BASE_URL = 'http://127.0.0.1:5175'
const API_URL = 'http://127.0.0.1:8000'

async function getFreshTokens(page) {
  const resp = await page.request.post(
    `${API_URL}/api/v1/auth/login`,
    { data: { username: 'admin', password: '1' } }
  )
  return resp.json()
}

export async function navigateToDevicePage(page) {
  // 1. Navigate to app origin first — localStorage only works on proper origins
  await page.goto(BASE_URL + '/', { waitUntil: 'domcontentloaded', timeout: 10000 })
  
  // 2. Get fresh tokens via Playwright HTTP API
  const tokens = await getFreshTokens(page)
  if (!tokens?.access_token) return
  
  // 3. Now on correct origin (http://127.0.0.1:5175), localStorage access works
  await page.evaluate((d) => {
    try {
      localStorage.clear()
      localStorage.setItem('access_token', d.token)
      localStorage.setItem('refresh_token', d.refresh)
    } catch {}
  }, { token: tokens.access_token, refresh: tokens.refresh_token })
  
  // 4. Navigate to the destination — React picks up token on init
  await page.goto(BASE_URL + '/device', { waitUntil: 'networkidle', timeout: 15000 })
  await page.waitForURL(/\/device\//, { timeout: 10000 }).catch(() => {})
  await page.waitForTimeout(2000)
}

export async function addDeviceViaRegisteredPage(page, name, ip, location = 'Test Location') {
  await page.getByRole('button', { name: 'Add Device' }).click()
  const manualBtn = page.getByRole('button', { name: 'Manual Setup' })
  await expect(manualBtn).toBeVisible({ timeout: 3000 })
  await manualBtn.click()

  const overlay = page.locator('div[style*=" 50"]').filter({ hasText: /Manual Setup/ })
  await expect(overlay).toBeVisible({ timeout: 5000 })

  const inputs = overlay.locator('input[type="text"]')
  await expect(inputs).toHaveCount(3, { timeout: 3000 })
  await inputs.nth(0).fill(name)
  await inputs.nth(1).fill(ip)
  await inputs.nth(2).fill(location)

  const submitBtn = overlay.getByRole('button').filter({ hasText: /Connect Device|Connect/ })
  await expect(submitBtn).toBeVisible({ timeout: 3000 }).catch(() => {})
  await submitBtn.click({ force: true })

  try { await expect(overlay).toBeHidden({ timeout: 8000 }) } catch {}
  await expect(page.locator('tbody tr').filter({ hasText: name })).toBeVisible({ timeout: 8000 })
}

export async function editDeviceViaRegisteredPage(page, oldName, newName) {
  const row = page.locator('tbody tr').filter({ hasText: oldName }).first()
  await row.click()
  await page.waitForTimeout(300)

  const editBtn = row.locator('button').filter({ hasText: /Edit|✏/ }).first()
  const editVisible = await editBtn.isVisible({ timeout: 1000 }).catch(() => false)
  if (editVisible) {
    await editBtn.click()
  } else {
    const allBtns = await row.locator('button').all()
    for (const b of allBtns) {
      if (await b.isVisible()) { await b.click(); await page.waitForTimeout(300); break }
    }
  }

  const overlay = page.locator('div[style*=" 50"]').filter({ hasText: /Edit Device/ })
  if (await overlay.isVisible({ timeout: 3000 }).catch(() => false)) {
    const inputs = overlay.locator('input[type="text"]')
    const count = await inputs.count().catch(() => 0)
    if (count >= 1) await inputs.nth(0).fill(newName)
    const sb = overlay.getByRole('button').filter({ hasText: /Save|Update/ })
    if (await sb.isVisible({ timeout: 2000 }).catch(() => false)) {
      await sb.click({ force: true })
    }
    try { await expect(overlay).toBeHidden({ timeout: 5000 }) } catch {}
  }

  await expect(page.locator('tbody').filter({ hasText: newName })).toBeVisible({ timeout: 5000 })
}

export async function deleteTestDevices(page) {
  try {
    let count = (await page.locator('tbody tr').count())
    for (let i = 0; i < Math.min(count, 20); i++) {
      const row = page.locator('tbody tr').first()
      const name = (await row.locator('td').first().textContent() || '').replace(/\s/g, '')
      if (name.startsWith('test_') || name.startsWith('test-') || name.includes('test')) {
        await row.scrollIntoViewIfNeeded()
        const delBtn = row.locator('button').filter({ hasText: /Delete|🗑|trash|✕|×/i }).first()
        const delVisible = await delBtn.isVisible({ timeout: 500 }).catch(() => false)
        if (delVisible) await delBtn.click()
        else {
          const btns = await row.locator('button').all()
          for (const b of btns) { if (await b.isVisible()) { await b.click(); break } }
        }
        const confirm = page.getByRole('button').filter({ hasText: /Delete|Confirm|Yes Delete/i }).first()
        if (await confirm.isVisible({ timeout: 1500 }).catch(() => false)) await confirm.click()
        try { await expect(row).toBeHidden({ timeout: 3000 }) } catch {}
      } else break
      await page.waitForTimeout(300)
      count = (await page.locator('tbody tr').count())
    }
  } catch {}
}
