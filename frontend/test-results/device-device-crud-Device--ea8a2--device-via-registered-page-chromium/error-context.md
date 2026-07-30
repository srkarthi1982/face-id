# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: device\device-crud.spec.ts >> Device CRUD >> add device via registered page
- Location: tests\device\device-crud.spec.ts:13:3

# Error details

```
Error: page.goto: net::ERR_ABORTED at http://127.0.0.1:5175/device
Call log:
  - navigating to "http://127.0.0.1:5175/device", waiting until "networkidle"

```

# Page snapshot

```yaml
- generic [ref=e1]:
  - generic [ref=e3]:
    - generic [ref=e4]:
      - button "EN" [ref=e5] [cursor=pointer]
      - button "AR" [ref=e6] [cursor=pointer]
    - generic [ref=e7]:
      - heading "JAC FACE ID" [level=1] [ref=e8]
      - paragraph [ref=e9]: Sign in to your account to continue
      - generic [ref=e10]:
        - generic [ref=e11]:
          - generic [ref=e12]: Username
          - generic [ref=e13]:
            - img
            - textbox [active] [ref=e14]
        - generic [ref=e15]:
          - generic [ref=e16]: Password
          - generic [ref=e17]:
            - img
            - textbox [ref=e18]
        - button "Login" [ref=e19] [cursor=pointer]
  - button "🔍 Inspect" [ref=e20] [cursor=pointer]
```

# Test source

```ts
  1   | import { test as base, expect } from '@playwright/test'
  2   | export const test = base
  3   | export { expect }
  4   | 
  5   | const BASE_URL = 'http://127.0.0.1:5175'
  6   | const API_URL = 'http://127.0.0.1:8000'
  7   | 
  8   | async function getFreshTokens(page) {
  9   |   const resp = await page.request.post(
  10  |     `${API_URL}/api/v1/auth/login`,
  11  |     { data: { username: 'admin', password: '1' } }
  12  |   )
  13  |   return resp.json()
  14  | }
  15  | 
  16  | export async function navigateToDevicePage(page) {
  17  |   // 1. Navigate to app origin first — localStorage only works on proper origins
  18  |   await page.goto(BASE_URL + '/', { waitUntil: 'domcontentloaded', timeout: 10000 })
  19  |   
  20  |   // 2. Get fresh tokens via Playwright HTTP API
  21  |   const tokens = await getFreshTokens(page)
  22  |   if (!tokens?.access_token) return
  23  |   
  24  |   // 3. Now on correct origin (http://127.0.0.1:5175), localStorage access works
  25  |   await page.evaluate((d) => {
  26  |     try {
  27  |       localStorage.clear()
  28  |       localStorage.setItem('access_token', d.token)
  29  |       localStorage.setItem('refresh_token', d.refresh)
  30  |     } catch {}
  31  |   }, { token: tokens.access_token, refresh: tokens.refresh_token })
  32  |   
  33  |   // 4. Navigate to the destination — React picks up token on init
> 34  |   await page.goto(BASE_URL + '/device', { waitUntil: 'networkidle', timeout: 15000 })
      |              ^ Error: page.goto: net::ERR_ABORTED at http://127.0.0.1:5175/device
  35  |   await page.waitForURL(/\/device\//, { timeout: 10000 }).catch(() => {})
  36  |   await page.waitForTimeout(2000)
  37  | }
  38  | 
  39  | export async function addDeviceViaRegisteredPage(page, name, ip, location = 'Test Location') {
  40  |   await page.getByRole('button', { name: 'Add Device' }).click()
  41  |   const overlay = page.locator('div[style*=" 50"]').filter({ hasText: /New Device/ })
  42  |   await expect(overlay).toBeVisible({ timeout: 5000 })
  43  | 
  44  |   const inputs = overlay.locator('input[type="text"]')
  45  |   await expect(inputs).toHaveCount(3, { timeout: 3000 })
  46  |   await inputs.nth(0).fill(name)
  47  |   await inputs.nth(1).fill(ip)
  48  |   await inputs.nth(2).fill(location)
  49  | 
  50  |   const submitBtn = overlay.getByRole('button').filter({ hasText: /Create Device|Add Device|Save Changes/ })
  51  |   await expect(submitBtn).toBeVisible({ timeout: 3000 }).catch(() => {})
  52  |   await submitBtn.click({ force: true })
  53  | 
  54  |   try { await expect(overlay).toBeHidden({ timeout: 8000 }) } catch {}
  55  |   await expect(page.locator('tbody tr').filter({ hasText: name })).toBeVisible({ timeout: 8000 })
  56  | }
  57  | 
  58  | export async function editDeviceViaRegisteredPage(page, oldName, newName) {
  59  |   const row = page.locator('tbody tr').filter({ hasText: oldName }).first()
  60  |   await row.click()
  61  |   await page.waitForTimeout(300)
  62  | 
  63  |   const editBtn = row.locator('button').filter({ hasText: /Edit|✏/ }).first()
  64  |   const editVisible = await editBtn.isVisible({ timeout: 1000 }).catch(() => false)
  65  |   if (editVisible) {
  66  |     await editBtn.click()
  67  |   } else {
  68  |     const allBtns = await row.locator('button').all()
  69  |     for (const b of allBtns) {
  70  |       if (await b.isVisible()) { await b.click(); await page.waitForTimeout(300); break }
  71  |     }
  72  |   }
  73  | 
  74  |   const overlay = page.locator('div[style*=" 50"]').filter({ hasText: /Edit Device/ })
  75  |   if (await overlay.isVisible({ timeout: 3000 }).catch(() => false)) {
  76  |     const inputs = overlay.locator('input[type="text"]')
  77  |     const count = await inputs.count().catch(() => 0)
  78  |     if (count >= 1) await inputs.nth(0).fill(newName)
  79  |     const sb = overlay.getByRole('button').filter({ hasText: /Save|Update/ })
  80  |     if (await sb.isVisible({ timeout: 2000 }).catch(() => false)) {
  81  |       await sb.click({ force: true })
  82  |     }
  83  |     try { await expect(overlay).toBeHidden({ timeout: 5000 }) } catch {}
  84  |   }
  85  | 
  86  |   await expect(page.locator('tbody').filter({ hasText: newName })).toBeVisible({ timeout: 5000 })
  87  | }
  88  | 
  89  | export async function deleteTestDevices(page) {
  90  |   try {
  91  |     let count = (await page.locator('tbody tr').count())
  92  |     for (let i = 0; i < Math.min(count, 20); i++) {
  93  |       const row = page.locator('tbody tr').first()
  94  |       const name = (await row.locator('td').first().textContent() || '').replace(/\s/g, '')
  95  |       if (name.startsWith('test_') || name.startsWith('test-') || name.includes('test')) {
  96  |         await row.scrollIntoViewIfNeeded()
  97  |         const delBtn = row.locator('button').filter({ hasText: /Delete|🗑|trash|✕|×/i }).first()
  98  |         const delVisible = await delBtn.isVisible({ timeout: 500 }).catch(() => false)
  99  |         if (delVisible) await delBtn.click()
  100 |         else {
  101 |           const btns = await row.locator('button').all()
  102 |           for (const b of btns) { if (await b.isVisible()) { await b.click(); break } }
  103 |         }
  104 |         const confirm = page.getByRole('button').filter({ hasText: /Delete|Confirm|Yes Delete/i }).first()
  105 |         if (await confirm.isVisible({ timeout: 1500 }).catch(() => false)) await confirm.click()
  106 |         try { await expect(row).toBeHidden({ timeout: 3000 }) } catch {}
  107 |       } else break
  108 |       await page.waitForTimeout(300)
  109 |       count = (await page.locator('tbody tr').count())
  110 |     }
  111 |   } catch {}
  112 | }
  113 | 
```