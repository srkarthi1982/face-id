import { test as setup } from '@playwright/test'

setup('authenticate as admin', async ({ page }) => {
  const res = await page.request.post('/api/v1/auth/login', {
    data: { username: 'admin', password: '1' },
  })
  const body = await res.json()
  const accessToken = (body as any)?.access_token
  const refreshToken = (body as any)?.refresh_token ?? ''

  if (!accessToken) {
    throw new Error('Login failed: no access_token returned')
  }

  await page.goto('/device')
  // Wait for navigation to the logged-in state (redirects to /device/registered)
  await page.waitForURL(/\/device/, { timeout: 10000 })
  await page.context().addCookies([
    {
      name: 'access_token',
      value: accessToken,
      domain: 'localhost',
      path: '/',
      httpOnly: false,
      secure: false,
      sameSite: 'Lax',
    },
  ])
  await page.evaluate((t: string) => localStorage.setItem('access_token', t), accessToken)
  if (refreshToken) {
    await page.evaluate((t: string) => localStorage.setItem('refresh_token', t), refreshToken)
  }
  await page.context().storageState({ path: 'tests/.auth/admin.json' })
})
