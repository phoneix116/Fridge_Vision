const express = require('express')
const { createProxyMiddleware } = require('http-proxy-middleware')
const cors = require('cors')
const path = require('path')

const app = express()
const PORT = process.env.PORT || 3000
const FASTAPI_URL = process.env.FASTAPI_URL || 'http://localhost:8000'

// Enable CORS for development
app.use(cors())

// Proxy /api/* → FastAPI, stripping the /api prefix
app.use(
  '/api',
  createProxyMiddleware({
    target: FASTAPI_URL,
    changeOrigin: true,
    pathRewrite: { '^/api': '' },
    // Pass multipart/form-data through without buffering
    on: {
      proxyReq: (proxyReq, req) => {
        // Log proxied requests
        console.log(`[proxy] ${req.method} ${req.url} → ${FASTAPI_URL}${req.url.replace(/^\/api/, '')}`)
      },
      error: (err, req, res) => {
        console.error('[proxy] error:', err.message)
        if (!res.headersSent) {
          res.status(502).json({
            error: 'Bad Gateway',
            detail: `Could not reach FastAPI at ${FASTAPI_URL}. Is it running?`,
          })
        }
      },
    },
  })
)

// Serve React build (production)
const distPath = path.join(__dirname, '..', 'frontend', 'dist')
app.use(express.static(distPath))

// SPA fallback — send index.html for any non-API route
app.get('*', (req, res) => {
  const indexPath = path.join(distPath, 'index.html')
  res.sendFile(indexPath, err => {
    if (err) {
      res.status(404).json({
        error: 'Frontend not built yet',
        hint: 'Run: cd frontend && npm install && npm run build',
      })
    }
  })
})

app.listen(PORT, () => {
  console.log(`\n🥗 Fridge Vision server running at http://localhost:${PORT}`)
  console.log(`   Proxying /api/* → ${FASTAPI_URL}`)
  console.log(`   Serving React build from: ${distPath}\n`)
})
