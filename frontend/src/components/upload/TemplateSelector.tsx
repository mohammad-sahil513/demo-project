import { useEffect, useState, useMemo } from 'react'
import { ChevronRight, Check, Eye, Loader2 } from 'lucide-react'
import { templateApi } from '../../api/templateApi'
import { useJobStore, type DocType, type Template } from '../../store/useJobStore'
import { TemplatePreviewModal } from '../templates/TemplatePreviewModal'

const DOC_ORDER: DocType[] = ['PDD', 'SDD', 'UAT']

function matchesType(tpl: Template, docType: DocType): boolean {
  const tt = (tpl.template_type || tpl.type || '').toUpperCase()
  return tt === docType
}

export function TemplateSelector() {
  const {
    selectedDocs,
    selectedTemplateByType,
    setSelectedTemplateForType,
  } = useJobStore()
  const [templates, setTemplates] = useState<Template[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [previewTemplate, setPreviewTemplate] = useState<Template | null>(null)

  const orderedSelected = useMemo(
    () => DOC_ORDER.filter((d) => selectedDocs.includes(d)),
    [selectedDocs]
  )

  const fetchTemplates = async () => {
    try {
      setLoading(true)
      const data = await templateApi.listTemplates()
      setTemplates(data)
    } catch {
      setError('Could not load templates. Is the backend running?')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchTemplates()
  }, [])

  if (loading) {
    return (
      <div className="space-y-6">
        {orderedSelected.map((doc) => (
          <div key={doc} className="grid grid-cols-2 gap-4">
            {[1, 2].map((i) => (
              <div key={i} className="border border-ey-border p-5 animate-pulse">
                <div className="h-4 bg-ey-border w-16 mb-3" />
                <div className="h-3 bg-ey-border w-full mb-2" />
              </div>
            ))}
          </div>
        ))}
      </div>
    )
  }

  if (error) {
    return (
      <div className="border border-ey-border p-6 text-center">
        <p className="font-body text-sm text-ey-muted">{error}</p>
        <button type="button" onClick={fetchTemplates} className="mt-3 font-body text-xs underline text-ey-ink-strong">
          Retry
        </button>
      </div>
    )
  }

  if (orderedSelected.length === 0) {
    return (
      <p className="font-body text-sm text-ey-muted">
        Select at least one output document type above to choose templates.
      </p>
    )
  }

  return (
    <div className="space-y-10">
      {orderedSelected.map((docType) => {
        const forType = templates.filter((t) => matchesType(t, docType))
        const selectedId = selectedTemplateByType[docType]

        return (
          <div key={docType}>
            <div className="flex items-center justify-between mb-4">
              <p className="font-body text-xs font-semibold tracking-widest uppercase text-ey-muted">
                {docType} template
              </p>
              {selectedId && (
                <button
                  type="button"
                  onClick={() => setSelectedTemplateForType(docType, null)}
                  className="font-body text-[11px] text-ey-muted underline hover:text-ey-ink-strong"
                >
                  Clear selection
                </button>
              )}
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {forType.map((tpl) => {
                const selected = selectedId === tpl.id
                const isReady = tpl.status === 'READY'
                const isProcessing = tpl.status === 'COMPILING' || tpl.status === 'PENDING'
                return (
                  <div
                    key={tpl.id}
                    onClick={() => isReady && setSelectedTemplateForType(docType, tpl.id)}
                    role="button"
                    tabIndex={isReady ? 0 : -1}
                    onKeyDown={(e) => {
                      if (isReady && (e.key === 'Enter' || e.key === ' ')) {
                        e.preventDefault()
                        setSelectedTemplateForType(docType, tpl.id)
                      }
                    }}
                    className={`p-5 border-2 text-left transition-all relative group focus:outline-none focus-visible:ring-2 focus-visible:ring-ey-primary focus-visible:ring-offset-2 ${
                      selected
                        ? 'border-ey-ink-strong bg-ey-ink-strong text-white'
                        : isReady
                          ? 'border-ey-border bg-white hover:border-ey-ink-strong'
                          : 'border-ey-border bg-ey-surface/60 opacity-90'
                    }`}
                  >
                    {selected && (
                      <div className="absolute top-3 right-3 w-5 h-5 bg-ey-primary text-ey-ink-strong flex items-center justify-center">
                        <Check size={11} strokeWidth={3} className="text-current" />
                      </div>
                    )}
                    <div
                      className={`inline-block px-2 py-0.5 mb-3 text-[10px] font-body font-semibold tracking-widest uppercase ${
                        tpl.is_custom
                          ? selected
                            ? 'bg-ey-primary text-ey-ink-strong'
                            : 'bg-ey-ink-strong text-ey-primary'
                          : selected
                            ? 'bg-white/20 text-white'
                            : 'bg-ey-surface text-ey-muted'
                      }`}
                    >
                      {tpl.is_custom ? 'Custom' : 'Standard'}
                    </div>
                    {isProcessing && (
                      <div className={`inline-flex items-center gap-1 px-2 py-0.5 mb-2 text-[10px] font-body font-semibold tracking-widest uppercase ${
                        selected ? 'bg-white/20 text-white' : 'bg-amber-100 text-amber-700'
                      }`}>
                        <Loader2 size={10} className="animate-spin" />
                        Processing
                      </div>
                    )}
                    <p
                      className={`font-display font-bold text-lg tracking-wide uppercase mb-1 truncate ${
                        selected ? 'text-ey-primary' : 'text-ey-ink-strong'
                      }`}
                    >
                      {tpl.filename}
                    </p>
                    <p
                      className={`font-body text-xs mb-2 truncate ${
                        selected ? 'text-white/60' : 'text-ey-muted'
                      }`}
                    >
                      {tpl.template_id}
                    </p>
                    {tpl.sections_preview?.length > 0 && (
                      <div className="space-y-1">
                        {tpl.sections_preview.slice(0, 3).map((s, i) => (
                          <div key={i} className="flex items-center gap-2">
                            <ChevronRight
                              size={10}
                              className={`shrink-0 ${selected ? 'text-ey-primary' : 'text-ey-muted'}`}
                            />
                            <span
                              className={`font-body text-xs truncate ${selected ? 'text-white/70' : 'text-ey-muted'}`}
                            >
                              {s}
                            </span>
                          </div>
                        ))}
                      </div>
                    )}
                    <div className="mt-4 pt-3 border-t border-black/10">
                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation()
                          if (isReady) setPreviewTemplate(tpl)
                        }}
                        disabled={!isReady}
                        className={`inline-flex items-center gap-1.5 font-body text-[11px] underline ${
                          !isReady
                            ? 'text-ey-muted/60 no-underline cursor-not-allowed'
                            : selected
                              ? 'text-white/80 hover:text-white'
                              : 'text-ey-muted hover:text-ey-ink-strong'
                        }`}
                      >
                        <Eye size={12} />
                        {isReady ? 'Preview' : 'Processing…'}
                      </button>
                    </div>
                  </div>
                )
              })}
            </div>
            {forType.length === 0 && (
              <p className="font-body text-xs text-amber-700 mt-2">
                No {docType} templates in the library. Upload one from the Templates page, then return and select it here.
              </p>
            )}
          </div>
        )
      })}
      {previewTemplate && (
        <TemplatePreviewModal
          template={previewTemplate}
          onClose={() => setPreviewTemplate(null)}
        />
      )}
    </div>
  )
}
