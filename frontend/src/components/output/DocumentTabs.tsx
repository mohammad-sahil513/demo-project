import { useJobStore, type DocType } from '../../store/useJobStore'

export function DocumentTabs() {
  const {
    documents,
    activDoc,
    setActiveDoc,
    workflowDetailByType,
    setActiveSectionId,
    setSectionContent,
  } = useJobStore()

  if (!documents.length) return null

  const selectTab = (type: DocType) => {
    setActiveDoc(type)
    const w = workflowDetailByType[type]
    const first = w?.assembled_document?.sections?.[0]
    if (first) {
      setActiveSectionId(first.section_id)
      setSectionContent(first.content ?? '_No content for this section._')
    } else {
      setActiveSectionId(null)
      setSectionContent(null)
    }
  }

  return (
    <div
      role="tablist"
      aria-label="Generated document types"
      className="flex w-full items-stretch gap-0 border-b border-ey-border bg-ey-surface/60"
    >
      {documents.map(({ type }) => {
        const active = activDoc === type
        return (
          <button
            key={type}
            type="button"
            role="tab"
            aria-selected={active}
            id={`doc-tab-${type}`}
            onClick={() => selectTab(type as DocType)}
            className={`relative min-w-[5.5rem] flex-1 max-w-[12rem] px-4 py-3.5 text-center font-body text-sm font-semibold uppercase tracking-wide transition-colors border-b-[3px] -mb-px focus:outline-none focus-visible:z-10 focus-visible:ring-2 focus-visible:ring-ey-primary focus-visible:ring-offset-2 focus-visible:ring-offset-white ${
              active
                ? 'text-ey-ink-strong border-ey-primary bg-white'
                : 'text-ey-muted border-transparent hover:text-ey-ink hover:bg-white/80'
            }`}
          >
            {type}
          </button>
        )
      })}
    </div>
  )
}
