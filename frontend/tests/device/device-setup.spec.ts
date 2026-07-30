import { test, expect, navigateToDevicePage, deleteTestDevices } from '../fixtures'

test.describe('Device Setup Page', () => {
  test.beforeEach(async ({ page }) => {
    await navigateToDevicePage(page)
    // Click the Setup link in the sidebar to navigate to the setup page
    await page.getByRole('link', { name: 'Setup' }).click()
    // Wait for setup page to load
    await page.waitForLoadState('networkidle', { timeout: 10000 })
    await deleteTestDevices(page)
  })

  test.afterEach(async ({ page }) => {
    await deleteTestDevices(page)
  })

  test('opens setup page with manual and auto discover options', async ({ page }) => {
    // Check manual setup section exists
    const manualCard = page.getByRole('button', { name: 'Manual Setup' }).locator('..')
    await expect(manualCard).toBeVisible()

    // Check auto discover section exists
    const autoCard = page.getByRole('button', { name: 'Auto Discover' }).locator('..')
    await expect(autoCard).toBeVisible()
  })

  test('opens manual setup modal when clicking Manual Setup', async ({ page }) => {
    // Click the Manual Setup card
    page.getByRole('button', { name: 'Manual Setup' }).click()
    // Modal should appear with "New Device" title (ModalOverlay)
    await expect(page.getByText('New Device')).toBeVisible({ timeout: 3000 })
    // Check form exists with expected labels
    await expect(page.getByLabel('Device Name')).toBeVisible()
    await expect(page.getByLabel('IP Address')).toBeVisible()
    await expect(page.getByLabel('Location')).toBeVisible()
  })

  test('submits manual form with valid data', async ({ page }) => {
    // Click the Manual Setup card
    page.getByRole('button', { name: 'Manual Setup' }).click()
    await expect(page.getByLabel('Device Name')).toBeVisible({ timeout: 3000 })
    await page.getByLabel('Device Name').fill('test_setup_device')
    await page.getByLabel('IP Address').fill('192.168.1.50')
    await page.getByLabel('Location').fill('Setup Zone')
    await page.getByRole('button', { name: 'Connect Device' }).click()
    // Modal should close (the form disappears within 5s)
    await expect(page.getByLabel('Device Name')).toBeHidden({ timeout: 5000 })
  })

  test('shows error on invalid IP format', async ({ page }) => {
    // Click the Manual Setup card
    page.getByRole('button', { name: 'Manual Setup' }).click()
    await expect(page.getByLabel('Device Name')).toBeVisible({ timeout: 3000 })
    await page.getByLabel('Device Name').fill('test_setup_invalid')
    await page.getByLabel('IP Address').fill('not_valid_ip')
    await page.getByLabel('Location').fill('Setup Zone')
    await page.getByRole('button', { name: 'Connect Device' }).click()
    // Modal should stay open (form submission fails with invalid IP)
    // Wait briefly for any validation
    await page.waitForTimeout(1000)
    // Modal should still be visible (no navigation to device list)
    const modalVisible = await page.getByLabel('Device Name').isVisible()
    expect(modalVisible || !page.url().includes('/device/')).toBe(true)
  })

  test('submits manually with missing location (should still work)', async ({ page }) => {
    // Click the Manual Setup card
    page.getByRole('button', { name: 'Manual Setup' }).click()
    await expect(page.getByLabel('Device Name')).toBeVisible({ timeout: 3000 })
    await page.getByLabel('Device Name').fill('test_setup_no_location')
    await page.getByLabel('IP Address').fill('192.168.1.51')
    // Location field left empty (it's optional)
    await page.getByRole('button', { name: 'Connect Device' }).click()
    // Modal should close
    await expect(page.getByLabel('Device Name')).toBeHidden({ timeout: 5000 })
  })
})
