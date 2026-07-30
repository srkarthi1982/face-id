# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: device\debug.spec.ts >> Debug >> check page loads
- Location: tests\device\debug.spec.ts:4:3

# Error details

```
Test timeout of 30000ms exceeded.
```

```
Error: locator.textContent: Test timeout of 30000ms exceeded.
Call log:
  - waiting for getByRole('button', { name: 'Add Device' })

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
  1  | import { test, expect } from '../fixtures'
  2  | 
  3  | test.describe('Debug', () => {
  4  |   test('check page loads', async ({ page }) => {
  5  |     await page.goto('/device')
  6  |     await page.waitForURL(/\/device\//, { timeout: 10000 })
  7  |     const url = page.url()
  8  |     const title = await page.title()
  9  |     console.log('URL:', url)
  10 |     console.log('TITLE:', title)
  11 |     // Dump the page content as a sanity check
  12 |     const h1s = await page.getByRole('heading', { level: 1 }).all()
  13 |     console.log('HEADINGS count:', h1s.length)
  14 |     for (const h of h1s) {
  15 |       console.log('HEADING:', await h.textContent())
  16 |     }
  17 |     const btns = await page.getByRole('button').all()
  18 |     console.log('BUTTONS count:', btns.length)
  19 |     for (const b of btns.slice(0, 5)) {
  20 |       console.log('BUTTON text:', await b.textContent())
  21 |     }
  22 |     // Check device form inputs
  23 |     const inputs = await page.locator('#device-form input[type="text"]').all()
  24 |     console.log('FORM INPUTS:', inputs.length)
  25 |     // Check the Add Device button
  26 |     const addBtn = page.getByRole('button', { name: 'Add Device' })
  27 |     console.log('ADD BUTTON visible:', await addBtn.isVisible())
> 28 |     console.log('ADD BUTTON text:', await addBtn.textContent())
     |                                                  ^ Error: locator.textContent: Test timeout of 30000ms exceeded.
  29 |     expect(true).toBe(true)
  30 |   })
  31 | })
  32 | 
```