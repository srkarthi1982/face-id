import { test, expect, navigateToDevicePage } from '../fixtures'

test('inspect add device modal DOM', async ({ page }) => {
  await navigateToDevicePage(page)
  
  await page.getByRole('button', { name: 'Add Device' }).click()
  
  // Give React time to render
  await page.waitForTimeout(1000)
  
  // Check what divs with fixed are present
  const fixedDivs = await page.locator('div.fixed').all()
  console.log('Fixed divs count:', fixedDivs.length)
  
  for (let i = 0; i < fixedDivs.length; i++) {
    const text = await fixedDivs[i].textContent()
    console.log(`Fixed div ${i}:`, text?.substring(0, 200))
  }
  
  // Check if #device-form exists
  const formCount = await page.locator('#device-form').count()
  console.log('#device-form count:', formCount)
  
  // Check buttons in page
  const buttons = await page.getByRole('button').all()
  console.log('All buttons:')
  for (const b of buttons) {
    const text = await b.textContent()
    const visible = await b.isVisible()
    console.log(`  "${text?.trim()}" visible=${visible}`)
  }
  
  // Check all inputs
  const inputs = await page.locator('input').all()
  console.log('All inputs count:', inputs.length)
  for (let i = 0; i < inputs.length; i++) {
    const type = await inputs[i].getAttribute('type')
    const id = await inputs[i].getAttribute('id')
    const name = await inputs[i].getAttribute('name')
    const visible = await inputs[i].isVisible()
    const inForm = await inputs[i].evaluate(el => el.form !== null)
    console.log(`  input[${i}] type=${type} id=${id} name=${name} visible=${visible} inForm=${inForm}`)
  }
  
  // Dump relevant HTML
  const modalHtml = await page.locator('div.fixed.inset-0').first().innerHTML()
  console.log('Modal HTML first 500 chars:', modalHtml?.substring(0, 500))
  
  expect(true).toBe(true)
})
