import { test, expect } from '../fixtures'

test.describe('Debug', () => {
  test('check page loads', async ({ page }) => {
    await page.goto('/device')
    await page.waitForURL(/\/device\//, { timeout: 10000 })
    const url = page.url()
    const title = await page.title()
    console.log('URL:', url)
    console.log('TITLE:', title)
    // Dump the page content as a sanity check
    const h1s = await page.getByRole('heading', { level: 1 }).all()
    console.log('HEADINGS count:', h1s.length)
    for (const h of h1s) {
      console.log('HEADING:', await h.textContent())
    }
    const btns = await page.getByRole('button').all()
    console.log('BUTTONS count:', btns.length)
    for (const b of btns.slice(0, 5)) {
      console.log('BUTTON text:', await b.textContent())
    }
    // Check device form inputs
    const inputs = await page.locator('#device-form input[type="text"]').all()
    console.log('FORM INPUTS:', inputs.length)
    // Check the Add Device button
    const addBtn = page.getByRole('button', { name: 'Add Device' })
    console.log('ADD BUTTON visible:', await addBtn.isVisible())
    console.log('ADD BUTTON text:', await addBtn.textContent())
    expect(true).toBe(true)
  })
})
