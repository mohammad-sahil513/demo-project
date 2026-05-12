/**
 * Schema + export-path-hint detail card on the template preview screen.
 *
 * The labels below mirror the values produced by
 * `modules.template.export_hint.compute_export_path_hint` on the
 * backend. Keep both sides in sync — adding a new hint string here
 * without a corresponding backend value means the UI will fall back to
 * displaying the raw key, which looks scary.
 */
const EXPORT_PATH_HINT_LABELS: Record<string, string> = {
  xlsx_or_other: 'XLSX / other (not custom DOCX path)',
  inbuilt_docx_builder: 'Inbuilt DOCX builder',
  native_placeholders: 'Export: native placeholders',
  strict_placeholder_filler: 'Export: strict placeholder filler',
  legacy_heading_fill: 'Export: legacy heading fill',
  blocked_require_native: 'Export blocked: native path required',
  blocked_legacy_disallowed: 'Export blocked: legacy disallowed',
}

interface Props {
  schemaVersion?: string | null
  placeholderSchema?: Record<string, unknown>
  resolvedSectionBindings?: Record<string, string[]>
  exportPathHint?: string | null
}

export function TemplateSchemaPanel({
  schemaVersion,
  placeholderSchema,
  resolvedSectionBindings,
  exportPathHint,
}: Props) {
  const placeholders = Array.isArray((placeholderSchema as { placeholders?: unknown[] } | undefined)?.placeholders)
    ? ((placeholderSchema as { placeholders: unknown[] }).placeholders)
    : []
  const boundSections = resolvedSectionBindings ? Object.keys(resolvedSectionBindings).length : 0
  const pathLabel =
    exportPathHint != null && exportPathHint !== ''
      ? EXPORT_PATH_HINT_LABELS[exportPathHint] ?? exportPathHint
      : null
  return (
    <div className="border border-ey-border bg-ey-surface/50 p-3">
      <p className="font-body text-[10px] tracking-widest uppercase text-ey-muted mb-2">Schema</p>
      {pathLabel && (
        <p className="font-body text-xs text-ey-ink-strong mb-2">
          <span className="text-ey-muted">Server export path:</span> {pathLabel}
        </p>
      )}
      <p className="font-body text-xs text-ey-ink-strong">Version: {schemaVersion ?? '—'}</p>
      <p className="font-body text-xs text-ey-ink-strong">Placeholders: {placeholders.length}</p>
      <p className="font-body text-xs text-ey-ink-strong">Sections bound: {boundSections}</p>
    </div>
  )
}

