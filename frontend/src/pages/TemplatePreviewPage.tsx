import { useCallback, useEffect, useRef, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { ArrowLeft, AlertCircle, Loader2 } from 'lucide-react'
import { useTemplatePreview } from '../components/templates/useTemplatePreview'
import { TemplatePreviewInfoPanel } from '../components/templates/TemplatePreviewInfoPanel'

export function TemplatePreviewPage() {
  const navigate = useNavigate()
  const { templateId } = useParams<{ templateId: string }>()
  const docxContainerRef = useRef<HTMLDivElement | null>(null)
  const { loading, error, dto, previewHtml, isXlsxPreview, reloadPreview } = useTemplatePreview({
    templateId: templateId || '',
  })

  const fetchTemplate = useCallback(async () => {
    await reloadPreview(docxContainerRef.current)
  }, [reloadPreview])

  useEffect(() => {
    fetchTemplate()
  }, [fetchTemplate])

  return (
    <div className="min-h-[calc(100vh-56px)] bg-ey-canvas">
      <div className="bg-ey-nav text-white px-8 py-8">
        <div className="max-w-5xl mx-auto flex items-center justify-between gap-4">
          <div className="flex items-center gap-4 min-w-0">
            <div className="w-1 h-10 bg-ey-primary shrink-0" />
            <div className="min-w-0">
              <p className="font-body text-xs tracking-widest uppercase text-ey-primary mb-1 font-medium">
                Template preview
              </p>
              <h1 className="font-display font-bold text-2xl uppercase tracking-tight truncate text-white">
                {dto?.template_type ?? 'Template'} — {templateId}
              </h1>
            </div>
          </div>
          <button
            type="button"
            onClick={() => navigate('/templates')}
            className="flex items-center gap-2 px-4 py-2 border border-white/20 text-white/80 hover:text-white hover:border-white/40 transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-ey-primary focus-visible:ring-offset-2 focus-visible:ring-offset-ey-nav"
          >
            <ArrowLeft size={14} />
            Back to Library
          </button>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-6 py-10">
        {loading ? (
          <div className="flex flex-col items-center justify-center min-h-[320px] gap-4">
            <Loader2 size={28} className="animate-spin text-ey-muted" />
            <p className="font-body text-sm text-ey-muted">Loading template…</p>
          </div>
        ) : error ? (
          <div className="flex flex-col items-center justify-center min-h-[320px] gap-4 px-8 text-center">
            <AlertCircle size={28} color="#DC2626" />
            <p className="font-body text-sm text-red-600">{error}</p>
            <button type="button" onClick={fetchTemplate} className="font-body text-xs underline text-ey-ink-strong">
              Retry
            </button>
          </div>
        ) : dto ? (
          <div className="bg-white w-full shadow-[0_1px_4px_rgba(0,0,0,0.08)] px-8 py-8 space-y-6">
            <TemplatePreviewInfoPanel dto={dto} isXlsxPreview={isXlsxPreview} />

            {isXlsxPreview ? (
              <div
                className="font-body text-sm text-ey-ink-strong [&_table]:w-full [&_table]:border-collapse [&_th]:border [&_th]:border-ey-border [&_th]:bg-ey-surface [&_th]:p-2 [&_th]:text-left [&_td]:border [&_td]:border-ey-border [&_td]:p-2"
                dangerouslySetInnerHTML={{ __html: previewHtml || '<div>No sheet preview available.</div>' }}
              />
            ) : (
              <div ref={docxContainerRef} className="docx-preview-host" />
            )}
          </div>
        ) : null}
      </div>
    </div>
  )
}
