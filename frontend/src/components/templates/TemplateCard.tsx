import { useState } from 'react'
import { Eye, Trash2, ChevronRight, AlertCircle, Loader2 } from 'lucide-react'
import { Template } from '../../store/useJobStore'
import { templateApi } from '../../api/templateApi'
import { TemplatePreviewModal } from './TemplatePreviewModal'
import { TemplateFidelityBadge } from './TemplateFidelityBadge'

interface Props {
  template: Template
  onDeleted: () => void
}

export function TemplateCard({ template, onDeleted }: Props) {
  const [showPreview, setShowPreview] = useState(false)
  const [confirmDelete, setConfirmDelete] = useState(false)
  const [deleting, setDeleting] = useState(false)
  const isReady = template.status === 'READY'
  const isProcessing = template.status === 'COMPILING' || template.status === 'PENDING'

  const handleDelete = async () => {
    setDeleting(true)
    try {
      await templateApi.deleteTemplate(template.id)
      onDeleted()
    } catch {
      setDeleting(false)
      setConfirmDelete(false)
    }
  }

  return (
    <>
      <div className="border border-ey-border bg-white hover:border-ey-ink-strong transition-all group animate-fade-in">
        <div className="h-1 bg-ey-primary" />

        <div className="p-5">
          <div className="flex items-start justify-between gap-3 mb-3">
            <div className="min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <span
                  className={`font-body text-[9px] font-semibold tracking-widest uppercase px-2 py-0.5 ${
                    template.is_custom
                      ? 'bg-ey-ink-strong text-ey-primary'
                      : 'bg-ey-canvas text-ey-muted'
                  }`}
                >
                  {template.is_custom ? 'Custom' : 'Standard'}
                </span>
                <TemplateFidelityBadge validationStatus={template.validation_status} />
                {isProcessing && (
                  <span className="inline-flex items-center gap-1 font-body text-[9px] font-semibold tracking-widest uppercase px-2 py-0.5 bg-amber-100 text-amber-700">
                    <Loader2 size={9} className="animate-spin" />
                    Processing
                  </span>
                )}
              </div>
              <h4 className="font-display font-bold text-lg uppercase tracking-wide text-ey-ink-strong leading-tight truncate">
                {template.filename}
              </h4>
              <p className="font-body text-[10px] text-ey-muted truncate">{template.template_id}</p>
            </div>
          </div>

          {template.description && (
            <p className="font-body text-xs text-ey-muted mb-4 leading-relaxed line-clamp-2">
              {template.description}
            </p>
          )}

          {template.status === 'FAILED' && (
            <div className="mb-4 border border-red-200 bg-red-50 px-3 py-2">
              <p className="font-body text-[11px] text-red-700 font-medium">Template compile failed</p>
              <p className="font-body text-[11px] text-red-600 mt-1">
                {template.compile_error || 'Compilation failed. Re-upload a corrected template.'}
              </p>
            </div>
          )}
          {isProcessing && (
            <div className="mb-4 border border-amber-200 bg-amber-50 px-3 py-2">
              <p className="font-body text-[11px] text-amber-700 font-medium">
                Template is compiling
              </p>
              <p className="font-body text-[11px] text-amber-700 mt-1">
                Preview will be available automatically after compilation completes.
              </p>
            </div>
          )}

          {template.sections_preview?.length > 0 && (
            <div className="space-y-1.5 mb-5">
              {template.sections_preview.slice(0, 4).map((s, i) => (
                <div key={i} className="flex items-center gap-2">
                  <ChevronRight size={10} className="shrink-0 text-ey-border" />
                  <span className="font-body text-xs text-ey-muted truncate">{s}</span>
                </div>
              ))}
              {template.sections_preview.length > 4 && (
                <p className="font-body text-[10px] text-ey-muted pl-4">
                  +{template.sections_preview.length - 4} more sections
                </p>
              )}
            </div>
          )}

          {confirmDelete ? (
            <div className="border border-red-200 bg-red-50 p-3 animate-fade-in">
              <div className="flex items-center gap-2 mb-3">
                <AlertCircle size={13} color="#DC2626" />
                <p className="font-body text-xs text-red-600 font-medium">Delete this template?</p>
              </div>
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={handleDelete}
                  disabled={deleting}
                  className="flex-1 py-1.5 bg-red-600 text-white font-body text-xs font-medium hover:bg-red-700 transition-colors"
                >
                  {deleting ? 'Deleting…' : 'Yes, Delete'}
                </button>
                <button
                  type="button"
                  onClick={() => setConfirmDelete(false)}
                  className="flex-1 py-1.5 border border-ey-border text-ey-ink-strong font-body text-xs hover:border-ey-ink-strong transition-colors"
                >
                  Cancel
                </button>
              </div>
            </div>
          ) : (
            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => isReady && setShowPreview(true)}
                disabled={!isReady}
                className={`flex-1 flex items-center justify-center gap-2 py-2.5 font-body text-xs font-medium transition-colors group focus:outline-none focus-visible:ring-2 focus-visible:ring-ey-primary focus-visible:ring-offset-2 ${
                  isReady
                    ? 'bg-ey-ink-strong text-white hover:bg-ey-ink'
                    : 'bg-ey-canvas text-ey-muted cursor-not-allowed'
                }`}
              >
                <Eye size={13} className={isReady ? 'group-hover:scale-110 transition-transform text-ey-primary' : ''} />
                {isReady ? 'Preview' : isProcessing ? 'Processing…' : 'Preview unavailable'}
              </button>
              {template.is_custom && (
                <button
                  type="button"
                  onClick={() => setConfirmDelete(true)}
                  className="w-10 flex items-center justify-center border border-ey-border text-ey-muted hover:border-red-300 hover:text-red-500 transition-colors"
                >
                  <Trash2 size={13} />
                </button>
              )}
            </div>
          )}
        </div>
      </div>
      {showPreview && (
        <TemplatePreviewModal
          template={template}
          onClose={() => setShowPreview(false)}
        />
      )}
    </>
  )
}
