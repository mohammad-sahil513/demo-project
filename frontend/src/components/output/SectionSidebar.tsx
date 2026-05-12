/**
 * Section sidebar on the Output page.
 *
 * Lists every section from the assembled document for the active
 * deliverable and highlights the currently selected one. Clicking a
 * row updates `activeSectionId` on the job store, which causes
 * {@link DocxViewer} to scroll/render that section's content.
 */
import { useJobStore } from '../../store/useJobStore'
import { ChevronRight } from 'lucide-react'
import { buildSectionPreviewMarkdown } from '../../utils/sectionPreviewContent'

export function SectionSidebar() {
  const {
    activDoc,
    activeSectionId,
    documents,
    workflowDetailByType,
    workflowRunByType,
    setActiveSectionId,
    setSectionContent,
  } = useJobStore()

  const currentDoc = documents.find((d) => d.type === activDoc)
  const assembled = activDoc ? workflowDetailByType[activDoc]?.assembled_document : null

  const rows =
    assembled?.sections?.map((s) => ({ section_id: s.section_id, title: s.title })) ??
    currentDoc?.sections ??
    []

  const handleSelect = (sectionId: string) => {
    if (!activDoc || sectionId === activeSectionId) return
    setActiveSectionId(sectionId)
    const row = assembled?.sections?.find((s) => s.section_id === sectionId)
    const runId = workflowRunByType[activDoc]
    const markdown =
      row && runId ? buildSectionPreviewMarkdown(row, runId) : null
    const fallback = (row?.content ?? '').trim() || null
    setSectionContent((markdown ?? fallback) ?? '_No content for this section._')
  }

  if (rows.length === 0) {
    return (
      <div className="p-6 text-center">
        <p className="font-body text-xs text-ey-muted">No sections available.</p>
      </div>
    )
  }

  return (
    <div className="flex flex-col">
      <div className="px-5 py-4 border-b border-ey-border">
        <p className="font-body text-[10px] tracking-widest uppercase text-ey-muted font-medium">
          Sections
        </p>
      </div>
      <div className="flex-1 overflow-y-auto">
        {rows.map((section, i) => {
          const active = activeSectionId === section.section_id
          return (
            <button
              key={section.section_id}
              type="button"
              onClick={() => handleSelect(section.section_id)}
              className={`w-full text-left px-5 py-3.5 flex items-center gap-3 border-b border-ey-border/60 transition-all group focus:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-ey-primary ${
                active ? 'bg-ey-ink-strong text-white' : 'hover:bg-ey-surface text-ey-ink-strong'
              }`}
            >
              <span
                className={`font-body text-[10px] font-medium w-5 shrink-0 ${
                  active ? 'text-ey-primary' : 'text-ey-muted'
                }`}
              >
                {String(i + 1).padStart(2, '0')}
              </span>
              <span
                className={`font-body text-sm flex-1 leading-snug ${
                  active ? 'text-white font-medium' : 'text-ey-ink'
                }`}
              >
                {section.title}
              </span>
              <ChevronRight
                size={13}
                className={`shrink-0 transition-transform ${
                  active ? 'text-ey-primary' : 'text-ey-border group-hover:text-ey-ink-strong'
                }`}
              />
            </button>
          )
        })}
      </div>
    </div>
  )
}
