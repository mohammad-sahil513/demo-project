interface Props {
  validationStatus?: string | null
  errors?: Array<Record<string, unknown>>
  warnings?: Array<Record<string, unknown>>
}

export function TemplateValidationPanel({ validationStatus, errors = [], warnings = [] }: Props) {
  return (
    <div className="border border-ey-border bg-white p-3">
      <p className="font-body text-[10px] tracking-widest uppercase text-ey-muted mb-2">Validation</p>
      <p className="font-body text-xs text-ey-ink-strong mb-2">Status: {validationStatus ?? 'unknown'}</p>
      {errors.length > 0 && (
        <div className="mb-2">
          <p className="font-body text-[11px] font-semibold text-red-700">Errors ({errors.length})</p>
          {errors.slice(0, 3).map((e, i) => (
            <p key={i} className="font-body text-[11px] text-red-600">
              {String(e.code || 'error')}: {String(e.message || 'Validation error')}
            </p>
          ))}
        </div>
      )}
      {warnings.length > 0 && (
        <div>
          <p className="font-body text-[11px] font-semibold text-amber-700">Warnings ({warnings.length})</p>
          {warnings.slice(0, 3).map((w, i) => (
            <p key={i} className="font-body text-[11px] text-amber-700">
              {String(w.code || 'warning')}: {String(w.message || 'Validation warning')}
            </p>
          ))}
        </div>
      )}
      {errors.length === 0 && warnings.length === 0 && (
        <p className="font-body text-[11px] text-ey-muted">No validation issues reported.</p>
      )}
    </div>
  )
}

