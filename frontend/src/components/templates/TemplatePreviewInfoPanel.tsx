import { FileText } from 'lucide-react'
import type { TemplateDto } from '../../api/types'

interface Props {
  dto: TemplateDto
  isXlsxPreview: boolean
}

export function TemplatePreviewInfoPanel({ dto, isXlsxPreview }: Props) {
  return (
    <>
      <div className="flex items-center gap-2 text-ey-muted">
        <FileText size={14} />
        <p className="font-body text-xs uppercase tracking-widest">
          {isXlsxPreview ? 'Spreadsheet view' : 'Document view'}
        </p>
      </div>

      <div className="border border-ey-border p-4 bg-ey-surface/50">
        <h3 className="font-body text-xs uppercase tracking-widest text-ey-muted mb-3">Metadata</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2 font-body text-xs text-ey-muted">
          <p><span className="font-semibold text-ey-ink-strong">ID:</span> {dto.template_id}</p>
          <p><span className="font-semibold text-ey-ink-strong">Type:</span> {dto.template_type ?? '—'}</p>
          <p><span className="font-semibold text-ey-ink-strong">Version:</span> {dto.version ?? '—'}</p>
          <p><span className="font-semibold text-ey-ink-strong">Status:</span> {dto.status}</p>
          <p><span className="font-semibold text-ey-ink-strong">Template source:</span> {dto.template_source ?? '—'}</p>
          <p><span className="font-semibold text-ey-ink-strong">Compiled at:</span> {dto.compiled_at ?? '—'}</p>
          <p><span className="font-semibold text-ey-ink-strong">Created:</span> {dto.created_at}</p>
          <p><span className="font-semibold text-ey-ink-strong">Updated:</span> {dto.updated_at}</p>
          <p><span className="font-semibold text-ey-ink-strong">Preview path:</span> {dto.preview_path ?? '—'}</p>
          <p><span className="font-semibold text-ey-ink-strong">Compile error:</span> {dto.compile_error ?? '—'}</p>
        </div>
      </div>
    </>
  )
}
