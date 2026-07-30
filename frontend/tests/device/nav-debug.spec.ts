import { test, expect } from '../fixtures'

test('check console errors', async ({ page }) => {
  const errors: string[] = []
  page.on('console', msg => {
    if (msg.type() === 'error') {
      errors.push(msg.text())
    }
  })
  await page.goto('/device')
  await page.waitForURL(/\/device\//, { timeout: 10000 })
  // Wait a bit for any JS errors
  await page.waitForTimeout(2000)
  console.log('ERRORS:', errors)
  console.log('URL:', page.url())
  
  // Check if page has any DOM content
  const body_html = await page.content()
  const hasContent = body_html.includes('Add Device') || 
                     body_html.includes('Device Name') ||
                     body_html.includes('Registered')
  console.log('Has content:', hasContent)
  console.log('HTML length:', body_html.length)
  
  expect(errors.length).toBeLessThan(5)
})
