import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './tests',
  testMatch: '**/*.spec.ts',
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: 0,
  workers: 1,
  timeout: 30000,
  expect: { timeout: 10000 },
  use: {
    baseURL: 'http://127.0.0.1:5175',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    // storageState removed — auth now handled fresh in fixtures.ts via addInitScript
  },
  projects: [
    {
      name: 'chromium',
      use: {
        browserName: 'chromium',
        // storageState: 'tests/.auth/admin.json', // removed
        launchOptions: {
          executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
          args: [
            '--disable-blink-features=AutomationControlled',
            '--no-first-run',
            '--no-default-browser-check',
          ],
        },
      },
    },
  ],
  reporter: process.env.CI ? 'blob' : 'list',
})
