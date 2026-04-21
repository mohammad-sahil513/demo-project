import { useState } from 'react'
import { Eye, Trash2, ChevronRight, AlertCircle } from 'lucide-react'
import { Template } from '../../store/useJobStore'
import { templateApi } from '../../api/templateApi'
import { TemplatePreviewModal } from './TemplatePreviewModal'

interface Props {
  template: Template
  onDeleted: () => void
}

export function TemplateCard({ template, onDeleted }: Props) {
  const [showPreview, setShowPreview] = useState(false)
  const [confirmDelete, setConfirmDelete] = useState(false)
  const [deleting, setDeleting] = useState(false)

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
                onClick={() => setShowPreview(true)}
                className="flex-1 flex items-center justify-center gap-2 py-2.5 bg-ey-ink-strong text-white font-body text-xs font-medium hover:bg-ey-ink transition-colors group focus:outline-none focus-visible:ring-2 focus-visible:ring-ey-primary focus-visible:ring-offset-2"
              >
                <Eye size={13} className="group-hover:scale-110 transition-transform text-ey-primary" />
                Preview
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
