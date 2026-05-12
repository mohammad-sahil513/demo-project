/**
 * Helpers that turn an assembled section row into the markdown blob
 * rendered by {@link DocxViewer} on the Output page.
 *
 * The exported DOCX embeds the diagram PNG from disk, but the markdown
 * preview only sees the section's `content` field. When `output_type`
 * is `"diagram"` we append a markdown image referencing the backend's
 * `/api/workflow-runs/{id}/sections/{section_id}/diagram` endpoint so
 * the preview matches the exported document.
 */
import { baseURL } from '../api/client'

/** Assembled section row from GET /workflow-runs/:id (may include diagram_path). */
export interface AssembledSectionPreviewRow {
  section_id: string
  title?: string
  content?: string | null
  output_type?: string | null
  diagram_path?: string | null
}

/**
 * Markdown for the output review pane: body text plus generated diagram image when present.
 * DOCX export embeds the same PNG from disk; the UI previously showed only `content`, which is often empty for diagrams.
 */
export function buildSectionPreviewMarkdown(
  row: AssembledSectionPreviewRow,
  workflowRunId: string,
): string | null {
  const raw = typeof row.content === 'string' ? row.content.trim() : ''
  const ot = String(row.output_type || 'text').toLowerCase()
  const diagramPath =
    typeof row.diagram_path === 'string' && row.diagram_path.trim() ? row.diagram_path.trim() : null
  const sid = String(row.section_id || '').trim()

  let body = raw
  if (ot === 'diagram' && diagramPath && sid && workflowRunId) {
    const alt = String(row.title || 'Diagram').replace(/]/g, '')
    const url = `${baseURL}/workflow-runs/${encodeURIComponent(workflowRunId)}/sections/${encodeURIComponent(sid)}/diagram`
    const fig = `![${alt}](${url})`
    body = body ? `${body}\n\n${fig}` : fig
  }

  if (body) return body
  if (ot === 'diagram' && !diagramPath) {
    return '_No diagram image was generated for this section (see export warnings)._'
  }
  return null
}
