import { createServer } from 'vite'
import path from 'path'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

async function start() {
  const server = await createServer({
    mode: 'development',
    root: __dirname,
    server: {
      port: 5175,
      strictPort: true,
      host: true,
      open: false,
    },
    appType: 'spa',
  })

  await server.listen()
  console.log('Vite running on http://localhost:5175')

  // Keep alive until exit
  process.on('SIGINT', () => {
    server.close()
    process.exit(0)
  })
  process.on('SIGTERM', () => {
    server.close()
    process.exit(0)
  })
}

start().catch(err => {
  console.error('Failed to start Vite:', err)
  process.exit(1)
})
