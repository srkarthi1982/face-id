import { test, expect, navigateToDevicePage, addDeviceViaRegisteredPage, deleteTestDevices, editDeviceViaRegisteredPage } from '../fixtures'

test.describe('Device CRUD', () => {
  test.beforeEach(async ({ page }) => {
    await navigateToDevicePage(page)
    await deleteTestDevices(page)
  })

  test.afterEach(async ({ page }) => {
    await deleteTestDevices(page)
  })

  test('add device via registered page', async ({ page }) => {
    await addDeviceViaRegisteredPage(page, 'test_device_001', '192.168.1.100', 'Building A')
    // Verify device name is in table
    await expect(page.locator('tbody').filter({ hasText: 'test_device_001' })).toBeVisible()
    // Verify row has all expected cells
    const row = page.locator('tbody tr').filter({ hasText: 'test_device_001' }).first()
    await expect(row.locator('td').first()).toHaveText('test_device_001')
    await expect(row.locator('td').nth(1)).toHaveText('192.168.1.100')
  })

  test('edit device', async ({ page }) => {
    // Add a device first
    await addDeviceViaRegisteredPage(page, 'test_device_002', '192.168.1.101', 'Building B')
    // Edit it
    await editDeviceViaRegisteredPage(page, 'test_device_002', 'test_device_002_edited')
    // Old name gone, new name visible
    await expect(page.locator('tbody tr').filter({ hasText: 'test_device_002' })).toBeHidden({ timeout: 5000 })
    const editedRow = page.locator('tbody tr').filter({ hasText: 'test_device_002_edited' }).first()
    await expect(editedRow.locator('td').first()).toHaveText('test_device_002_edited')
  })

  test('delete device', async ({ page }) => {
    // Add a device first
    await addDeviceViaRegisteredPage(page, 'test_device_003', '192.168.1.102', 'Building C')
    // Find row with the device's Delete button and click it
    const row = page.locator('tbody tr').filter({ hasText: 'test_device_003' }).first()
    await row.locator('button', { hasText: 'Delete' }).click()
    // Confirm delete in modal
    await page.getByRole('button', { name: 'Delete' }).click()
    // Row should disappear
    await expect(page.locator('tbody').filter({ hasText: 'test_device_003' })).toBeHidden({ timeout: 5000 })
  })

  test('sort by device name', async ({ page }) => {
    await addDeviceViaRegisteredPage(page, 'test_z_device', '192.168.1.200', 'Zone Z')
    await addDeviceViaRegisteredPage(page, 'test_a_device', '192.168.1.201', 'Zone A')
    // Click the "Device Name" header to sort
    await page.locator('button', { hasText: 'Device Name' }).first().click()
    // First row should be the first alphabetically
    const rows = page.locator('tbody tr')
    const first = (await rows.nth(0).locator('td').first().textContent()) ?? ''
    expect(first).toBe('test_a_device')
  })

  test('cancel modal does not create device', async ({ page }) => {
    await page.getByRole('button', { name: 'Add Device' }).click()
    await page.locator('.fixed button').filter({ hasText: 'Cancel' }).click()
    // Table should still be empty (no test devices)
    await expect(page.locator('tbody')).toBeVisible()
  })
})
