/**
 * Output page (route: `/output`).
 *
 * Renders the final generated document for every deliverable produced
 * by the workflow. Layout: a left-hand {@link DocumentTabs} switcher,
 * a {@link SectionSidebar} listing assembled sections, the
 * {@link DocxViewer} preview in the middle, and an evidence
 * {@link CitationPanel} on the right with a {@link DownloadPanel}
 * floating on top for the .docx/.xlsx export.
 *
 * On mount the page hydrates `workflowDetailByType` in the job store
 * from `/api/workflow-runs/{id}` so the user can reload safely without
 * losing context.
 */
import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Plus } from 'lucide-react'
import { DocumentTabs } from '../components/output/DocumentTabs'
import { SectionSidebar } from '../components/output/SectionSidebar'
import { DocxViewer } from '../components/output/DocxViewer'
import { DownloadPanel } from '../components/output/DownloadPanel'
import { CitationPanel } from '../components/output/CitationPanel'
import { useJobStore, type DocType } from '../store/useJobStore'
import { getWorkflow } from '../api/workflowApi'
import type { CitationDto } from '../api/types'
import { getApiErrorMessage } from '../api/errors'
import { buildSectionPreviewMarkdown } from '../utils/sectionPreviewContent'

export function OutputPage() {
  const navigate = useNavigate()
  const {
    selectedDocs,
    workflowRunByType,
    documents,
    activDoc,
    activeSectionId,
    workflowDetailByType,
    setDocuments,
    setWorkflowDetail,
    setActiveDoc,
    setActiveSectionId,
    setSectionContent,
  } = useJobStore()
  const [showAllWarnings, setShowAllWarnings] = useState(false)
  const [loadError, setLoadError] = useState<string | null>(null)
  const [reloadKey, setReloadKey] = useState(0)

  const citationRows = useMemo((): CitationDto[] => {
    if (!activDoc || !activeSectionId) return []
    const bundle = workflowDetailByType[activDoc]?.section_retrieval_results?.[activeSectionId]
    return bundle?.citations ?? []
  }, [activDoc, activeSectionId, workflowDetailByType])
  const activeWarnings = useMemo(() => {
    if (!activDoc) return []
    return (workflowDetailByType[activDoc]?.warnings ?? []) as Array<Record<string, unknown>>
  }, [activDoc, workflowDetailByType])
  const activeRunId = activDoc ? workflowRunByType[activDoc] : undefined
  const visibleWarnings = showAllWarnings ? activeWarnings : activeWarnings.slice(0, 4)

  useEffect(() => {
    const hasRuns = selectedDocs.some((d) => workflowRunByType[d])
    if (!hasRuns) {
      navigate('/')
      return
    }

    let cancelled = false
    setLoadError(null)
    ;(async () => {
      try {
        const docs: { type: DocType; sections: { section_id: string; title: string }[] }[] = []
        for (const doc of selectedDocs) {
          const runId = workflowRunByType[doc]
          if (!runId) continue
          const w = await getWorkflow(runId)
          if (cancelled) return
          setWorkflowDetail(doc, w)
          docs.push({
            type: doc,
            sections:
              w.assembled_document?.sections?.map((s) => ({
                section_id: s.section_id,
                title: s.title,
              })) ?? [],
          })
        }
        if (cancelled) return
        setDocuments(docs)
        if (docs.length > 0) {
          const firstType = docs[0].type
          setActiveDoc(firstType)
          const wf = useJobStore.getState().workflowDetailByType[firstType]
          const sec = wf?.assembled_document?.sections?.[0]
          const rid = workflowRunByType[firstType]
          if (sec) {
            setActiveSectionId(sec.section_id)
            const md = rid ? buildSectionPreviewMarkdown(sec, rid) : null
            const fb = (sec.content ?? '').trim() || null
            setSectionContent((md ?? fb) ?? '_No content for this section._')
          }
        }
      } catch (e: unknown) {
        if (!cancelled) {
          setLoadError(getApiErrorMessage(e, 'Could not load workflow output.'))
        }
      }
    })()

    return () => {
      cancelled = true
    }
  }, [
    navigate,
    selectedDocs,
    workflowRunByType,
    reloadKey,
    setDocuments,
    setWorkflowDetail,
    setActiveDoc,
    setActiveSectionId,
    setSectionContent,
  ])

  return (
    <div className="h-[calc(100vh-56px)] flex flex-col bg-white">
      <div className="flex items-center justify-between px-8 py-5 border-b border-ey-border bg-white shrink-0">
        <div className="flex items-center gap-4 min-w-0">
          <img
            src="/brand/ey-logo.svg"
            alt="AI SDLC"
            className="h-8 w-auto shrink-0 hidden sm:block opacity-90"
            width={132}
            height={28}
          />
          <div className="min-w-0">
            <p className="font-body text-[10px] tracking-widest uppercase text-ey-muted font-medium mb-1">
              Generated Output
            </p>
            <h1 className="font-display font-bold text-2xl uppercase text-ey-ink-strong tracking-tight leading-none">
              Document Review
            </h1>
          </div>
        </div>
        <button
          type="button"
          onClick={() => navigate('/')}
          className="flex items-center gap-2 border border-ey-border px-4 py-2.5 hover:border-ey-ink-strong transition-colors group focus:outline-none focus-visible:ring-2 focus-visible:ring-ey-primary focus-visible:ring-offset-2"
        >
          <Plus size={14} className="group-hover:rotate-90 transition-transform text-ey-ink" />
          <span className="font-body text-xs font-medium text-ey-ink-strong">New Job</span>
        </button>
      </div>

      {loadError && (
        <div className="px-8 py-3 border-b border-red-200 bg-red-50 shrink-0 flex flex-wrap items-center gap-3">
          <p className="font-body text-sm text-red-700 flex-1 min-w-0">{loadError}</p>
          <button
            type="button"
            onClick={() => setReloadKey((k) => k + 1)}
            className="font-body text-xs font-semibold underline text-red-800 shrink-0 focus:outline-none focus-visible:ring-2 focus-visible:ring-red-600 focus-visible:ring-offset-2"
          >
            Retry
          </button>
        </div>
      )}

      {documents.length > 0 && (
        <div className="px-8 bg-white shrink-0">
          <DocumentTabs />
          {activeWarnings.length > 0 && (
            <div className="mt-3 mb-3 border border-amber-200 bg-amber-50 px-4 py-3">
              <p className="font-body text-[11px] font-semibold text-amber-800 uppercase tracking-widest mb-1">
                Export warnings
              </p>
              <p className="font-body text-xs text-amber-800 mb-1">
                Showing {visibleWarnings.length} of {activeWarnings.length} warnings
              </p>
              {visibleWarnings.map((row, idx) => {
                const code = String(row.code || 'warning')
                const isBlocking = ['schema_mismatch', 'missing_required_columns'].includes(code.toLowerCase())
                return (
                  <p key={idx} className={`font-body text-xs ${isBlocking ? 'text-red-700 font-semibold' : 'text-amber-700'}`}>
                    [{code}] {String(row.message || row.error || 'See diagnostics for details.')}
                    {activeRunId && (
                      <>
                        {' '}
                        <a
                          href={`/api/workflow-runs/${activeRunId}/diagnostics`}
                          target="_blank"
                          rel="noreferrer"
                          className="underline"
                        >
                          diagnostics
                        </a>
                      </>
                    )}
                  </p>
                )
              })}
              {activeWarnings.length > 4 && (
                <button
                  type="button"
                  onClick={() => setShowAllWarnings((v) => !v)}
                  className="mt-1 font-body text-xs font-semibold underline text-amber-800"
                >
                  {showAllWarnings ? 'Show less' : 'Show all'}
                </button>
              )}
            </div>
          )}
        </div>
      )}

      <div className="flex flex-1 overflow-hidden">
        <div className="w-56 shrink-0 border-r border-ey-border overflow-y-auto bg-white">
          <SectionSidebar />
        </div>

        <div className="flex-1 flex min-w-0 overflow-hidden">
          <div className="flex-1 flex flex-col overflow-hidden min-w-0">
            <DocxViewer />
          </div>
          <CitationPanel citations={citationRows} />
        </div>
      </div>

      <DownloadPanel />
    </div>
  )
}
