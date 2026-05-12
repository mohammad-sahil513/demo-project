/**
 * Modal dialog that previews a template without leaving the current page.
 *
 * Used from the upload page's {@link TemplateSelector} and the
 * templates list page. Renders the DOCX preview inline via the shared
 * {@link useTemplatePreview} hook, or the HTML preview for XLSX
 * templates, along with the schema + validation panels.
 *
 * Closes on Escape, on backdrop click, and on the explicit close
 * button — the `useEffect` registers/removes the key listener exactly
 * once per mount.
 */
import { useEffect, useCallback, useRef } from 'react'
import { X, Loader2, AlertCircle } from 'lucide-react'
import { Template } from '../../store/useJobStore'
import { TemplateSchemaPanel } from './TemplateSchemaPanel'
import { TemplateValidationPanel } from './TemplateValidationPanel'
import { useTemplatePreview } from './useTemplatePreview'
import { TemplatePreviewInfoPanel } from './TemplatePreviewInfoPanel'

interface Props {
  template: Template
  onClose: () => void
}

export function TemplatePreviewModal({ template, onClose }: Props) {
  const docxContainerRef = useRef<HTMLDivElement | null>(null)
  const { loading, error, dto, previewHtml, isXlsxPreview, reloadPreview } = useTemplatePreview({
    templateId: template.id,
    fallbackTemplateType: template.type,
  })

  const fetchPreview = useCallback(async () => {
    await reloadPreview(docxContainerRef.current)
  }, [reloadPreview])

  useEffect(() => {
    fetchPreview()
    document.body.style.overflow = 'hidden'
    return () => {
      document.body.style.overflow = ''
    }
  }, [fetchPreview])

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [onClose])

  const titleType = dto?.template_type || template.type || template.id
  const schemaItems = ((dto?.sheet_map as { schema?: Array<Record<string, unknown>> } | undefined)?.schema ?? [])

  return (
    <div
      className="fixed inset-0 z-50 flex items-stretch bg-black/75"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose()
      }}
    >
      <div className="relative flex flex-col w-full max-w-6xl mx-auto my-6 bg-white shadow-2xl animate-slide-up">
        <div className="bg-ey-nav flex items-center gap-4 px-8 py-5 shrink-0">
          <div className="w-2 h-10 shrink-0 bg-ey-primary" />
          <div className="flex-1 min-w-0">
            <p className="font-body text-[10px] tracking-widest uppercase font-medium mb-0.5 text-ey-primary">
              Template preview
            </p>
            <h2 className="font-display font-bold text-2xl uppercase text-white tracking-tight leading-none truncate">
              {titleType} — {template.id}
            </h2>
          </div>
          <span
            className={`font-body text-[10px] font-semibold tracking-widest uppercase px-3 py-1 shrink-0 ${
              template.is_custom ? 'bg-ey-primary text-ey-ink-strong' : 'bg-white/10 text-white/70'
            }`}
          >
            {template.is_custom ? 'Custom' : 'Standard'}
          </span>
          <button
            type="button"
            onClick={onClose}
            className="w-9 h-9 flex items-center justify-center text-white/50 hover:text-white hover:bg-white/10 transition-colors shrink-0 ml-2 focus:outline-none focus-visible:ring-2 focus-visible:ring-ey-primary rounded-sm"
          >
            <X size={18} />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto bg-ey-canvas min-h-[420px]">
          {loading ? (
            <div className="flex flex-col items-center justify-center h-full min-h-[320px] gap-4">
              <Loader2 size={28} className="animate-spin text-ey-muted" />
              <p className="font-body text-sm text-ey-muted">Loading template preview…</p>
            </div>
          ) : error ? (
            <div className="flex flex-col items-center justify-center min-h-[320px] gap-4 px-8 text-center">
              <AlertCircle size={28} color="#DC2626" />
              <p className="font-body text-sm text-red-600">{error}</p>
              <button type="button" onClick={fetchPreview} className="font-body text-xs underline text-ey-ink-strong">
                Retry
              </button>
            </div>
          ) : (
            <div className="py-10 px-6">
              <div className="bg-white w-full max-w-[980px] mx-auto shadow-[0_1px_4px_rgba(0,0,0,0.08)] px-8 py-8 animate-fade-in">
                {dto && <TemplatePreviewInfoPanel dto={dto} isXlsxPreview={isXlsxPreview} />}
                {isXlsxPreview ? (
                  <div className="space-y-4">
                    <div
                      className="font-body text-sm text-ey-ink-strong [&_table]:w-full [&_table]:border-collapse [&_th]:border [&_th]:border-ey-border [&_th]:bg-ey-surface [&_th]:p-2 [&_th]:text-left [&_td]:border [&_td]:border-ey-border [&_td]:p-2"
                      dangerouslySetInnerHTML={{ __html: previewHtml || '<div>No sheet preview available.</div>' }}
                    />
                    {schemaItems.length > 0 && (
                      <div className="border border-ey-border bg-ey-surface/60 p-4">
                        <p className="font-body text-xs uppercase tracking-widest text-ey-muted mb-3">Schema summary</p>
                        <div className="space-y-3">
                          {schemaItems.map((item, idx) => {
                            const sheetName = String(item.sheet_name || item.name || `Sheet ${idx + 1}`)
                            const headers = Array.isArray(item.headers) ? item.headers : []
                            const required = Array.isArray(item.required_columns) ? item.required_columns : headers
                            const detectionMeta =
                              item && typeof item === 'object' && 'header_detection_metadata' in item
                                ? (item as { header_detection_metadata?: Record<string, unknown> }).header_detection_metadata
                                : undefined
                            const missingRequired = required.filter((r) => !headers.includes(r))
                            return (
                              <div key={`${sheetName}-${idx}`} className="font-body text-xs text-ey-ink-strong">
                                <p className="font-semibold">{sheetName}</p>
                                <p>Headers: {headers.length ? headers.join(', ') : 'None detected'}</p>
                                <p>Required: {required.length ? required.join(', ') : 'None'}</p>
                                {missingRequired.length > 0 && (
                                  <p className="text-amber-700">Missing required: {missingRequired.join(', ')}</p>
                                )}
                                {detectionMeta && (
                                  <p className="text-ey-muted">
                                    Detection: {String(detectionMeta.mode || 'n/a')} row{' '}
                                    {String(detectionMeta.selected_row || 'n/a')}
                                  </p>
                                )}
                              </div>
                            )
                          })}
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="space-y-4">
                    <div ref={docxContainerRef} className="docx-preview-host" />
                    {dto && (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        <TemplateSchemaPanel
                          schemaVersion={dto.schema_version}
                          placeholderSchema={dto.placeholder_schema}
                          resolvedSectionBindings={dto.resolved_section_bindings}
                          exportPathHint={dto.export_path_hint}
                        />
                        <TemplateValidationPanel
                          validationStatus={dto.validation_status}
                          errors={dto.validation_errors}
                          warnings={dto.validation_warnings}
                        />
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        <div className="border-t border-ey-border bg-white px-8 py-4 flex items-center justify-between shrink-0">
          <p className="font-body text-xs text-ey-muted">
            Press <kbd className="font-mono bg-ey-canvas px-1.5 py-0.5 text-[10px]">Esc</kbd> to close
          </p>
          <button
            type="button"
            onClick={onClose}
            className="font-body text-xs font-medium px-6 py-2.5 bg-ey-ink-strong text-white hover:bg-ey-ink transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-ey-primary focus-visible:ring-offset-2"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  )
}
