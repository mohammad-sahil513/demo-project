/**
 * Top-level router and layout shell.
 *
 * Routes (all rendered under the persistent {@link Navbar}):
 *
 * - `/`                                    Upload page (pick BRD + template).
 * - `/progress`                            Live workflow progress via SSE.
 * - `/output`                              Final exported document review.
 * - `/templates`                           Manage custom templates.
 * - `/templates/:templateId/preview`       Template preview detail view.
 *
 * Pages are loaded lazily with `React.lazy` so each route is its own
 * chunk in the production build — keeps the initial bundle small.
 */
import { Suspense, lazy } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Navbar } from './components/layout/Navbar'

const UploadPage = lazy(() => import('./pages/UploadPage').then((m) => ({ default: m.UploadPage })))
const ProgressPage = lazy(() => import('./pages/ProgressPage').then((m) => ({ default: m.ProgressPage })))
const OutputPage = lazy(() => import('./pages/OutputPage').then((m) => ({ default: m.OutputPage })))
const TemplatesPage = lazy(() => import('./pages/TemplatesPage').then((m) => ({ default: m.TemplatesPage })))
const TemplatePreviewPage = lazy(() =>
  import('./pages/TemplatePreviewPage').then((m) => ({ default: m.TemplatePreviewPage })),
)

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-white">
        <Navbar />
        <Suspense
          fallback={
            <div className="px-8 py-10">
              <p className="font-body text-sm text-ey-muted">Loading page…</p>
            </div>
          }
        >
          <Routes>
            <Route path="/" element={<UploadPage />} />
            <Route path="/progress" element={<ProgressPage />} />
            <Route path="/output" element={<OutputPage />} />
            <Route path="/templates" element={<TemplatesPage />} />
            <Route path="/templates/:templateId/preview" element={<TemplatePreviewPage />} />
          </Routes>
        </Suspense>
      </div>
    </BrowserRouter>
  )
}
