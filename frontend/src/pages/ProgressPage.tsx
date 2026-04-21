import { useEffect, useRef, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowRight, RefreshCw, AlertCircle } from 'lucide-react'
import { ProgressBar } from '../components/progress/ProgressBar'
import { useJobStore, type DocType } from '../store/useJobStore'
import { getWorkflowStatus, getWorkflow, subscribeToWorkflowEvents } from '../api/workflowApi'

const POLL_DEBOUNCE_MS = 320
/** If every SSE connection is still CLOSED after this delay following an error, use polling only. */
const SSE_ALL_CLOSED_CHECK_MS = 2000
/** While SSE is primary, full poll occasionally so quiet workflows stay fresh. */
const SSE_SAFETY_POLL_MS = 30_000

type WorkflowRunStatus = Awaited<ReturnType<typeof getWorkflowStatus>>

function docTypeForWorkflowRunId(
  runs: Partial<Record<DocType, string>>,
  workflowRunId: string
): DocType | undefined {
  return (['PDD', 'SDD', 'UAT'] as const).find((d) => runs[d] === workflowRunId)
}

function backendStatusUi(s: string | undefined): 'running' | 'completed' | 'failed' {
  const u = (s || '').toUpperCase()
  if (u === 'FAILED') return 'failed'
  if (u === 'COMPLETED') return 'completed'
  return 'running'
}

export function ProgressPage() {
  const navigate = useNavigate()
  const {
    selectedDocs,
    workflowRunByType,
    status,
    progress,
    currentStep,
    errorMessage,
    perTypeProgress,
    perTypeStep,
    setProgress,
    setStatus,
    setPerTypeProgress,
    setDocuments,
    setActiveDoc,
    setError,
    setWorkflowDetail,
    documents,
  } = useJobStore()

  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const statusByDocRef = useRef<Partial<Record<DocType, WorkflowRunStatus>>>({})
  const pollRef = useRef<() => Promise<void>>(async () => {})

  const loadCompletedOutputs = useCallback(async () => {
    const { selectedDocs: docs, workflowRunByType: runs, setWorkflowDetail, setDocuments, setActiveDoc } =
      useJobStore.getState()
    const out: { type: DocType; sections: { section_id: string; title: string }[] }[] = []
    for (const doc of docs) {
      const runId = runs[doc]
      if (!runId) continue
      const w = await getWorkflow(runId)
      setWorkflowDetail(doc, w)
      out.push({
        type: doc,
        sections:
          w.assembled_document?.sections?.map((s) => ({
            section_id: s.section_id,
            title: s.title,
          })) ?? [],
      })
    }
    setDocuments(out)
    if (out.length > 0) setActiveDoc(out[0].type)
  }, [])

  const reconcileFromSnapshot = useCallback(async () => {
    const { selectedDocs: docs, workflowRunByType: runs } = useJobStore.getState()
    if (docs.length === 0) return

    const snap = statusByDocRef.current
    const denom = docs.filter((d) => runs[d]).length
    let snapshotIncomplete = false
    let sumProgress = 0
    const stepParts: string[] = []
    let anyFailed = false

    for (const doc of docs) {
      if (!runs[doc]) continue
      const st = snap[doc]
      if (!st) {
        snapshotIncomplete = true
        sumProgress += 0
        stepParts.push(`${doc}: …`)
        setPerTypeProgress(doc, 0, 'Waiting for status…')
        continue
      }

      const p = st.overall_progress_percent ?? 0
      sumProgress += p
      const label = st.current_step_label || st.current_phase || '…'
      stepParts.push(`${doc}: ${label}`)
      setPerTypeProgress(doc, p, label)

      if (backendStatusUi(st.status) === 'failed') anyFailed = true
    }

    const avgProgress = denom > 0 ? Math.round(sumProgress / denom) : 0

    setProgress(avgProgress, stepParts.join(' · '))

    if (anyFailed) {
      const failedDoc = docs.find((doc) => {
        const st = snap[doc]
        return st && backendStatusUi(st.status) === 'failed'
      })
      setError(
        failedDoc
          ? `Pipeline failed (${failedDoc}). Check backend logs.`
          : 'Pipeline failed. Check backend logs.'
      )
      setStatus('failed')
      if (intervalRef.current) clearInterval(intervalRef.current)
      intervalRef.current = null
      return
    }

    const allCompleted =
      docs.length > 0 &&
      docs.every((d) => {
        const st = snap[d]
        return runs[d] && st && backendStatusUi(st.status) === 'completed'
      })

    if (allCompleted && docs.every((d) => runs[d])) {
      setStatus('completed')
      try {
        await loadCompletedOutputs()
      } catch {
        /* ignore */
      }
      if (intervalRef.current) clearInterval(intervalRef.current)
      intervalRef.current = null
      return
    }

    setStatus('running')

    if (snapshotIncomplete) {
      void pollRef.current()
    }
  }, [setProgress, setPerTypeProgress, setStatus, setError, loadCompletedOutputs])

  const poll = useCallback(async () => {
    const { selectedDocs: docs, workflowRunByType: runs } = useJobStore.getState()
    if (docs.length === 0) return
    try {
      const results = await Promise.all(
        docs.map(async (doc) => {
          const id = runs[doc]
          if (!id) return { doc, st: null as WorkflowRunStatus | null }
          const st = await getWorkflowStatus(id)
          return { doc, st }
        })
      )

      for (const { doc, st } of results) {
        if (st) statusByDocRef.current[doc] = st
      }

      await reconcileFromSnapshot()
    } catch {
      // network hiccup
    }
  }, [reconcileFromSnapshot])

  pollRef.current = poll

  const refreshSingleRun = useCallback(
    async (workflowRunId: string) => {
      const { workflowRunByType: runs } = useJobStore.getState()
      const doc = docTypeForWorkflowRunId(runs, workflowRunId)
      if (!doc) return
      try {
        const st = await getWorkflowStatus(workflowRunId)
        statusByDocRef.current[doc] = st
        await reconcileFromSnapshot()
      } catch {
        void poll()
      }
    },
    [reconcileFromSnapshot, poll]
  )

  const startPolling = useCallback(() => {
    void poll()
    intervalRef.current = setInterval(() => {
      void poll()
    }, 2500)
  }, [poll])

  const stopPolling = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
      intervalRef.current = null
    }
  }

  useEffect(() => {
    const { selectedDocs: docs, workflowRunByType: runs } = useJobStore.getState()
    const hasRuns = docs.length > 0 && docs.every((d) => runs[d])
    if (!hasRuns) {
      navigate('/')
      return
    }
    if (status !== 'running') {
      return () => {}
    }

    let cancelled = false
    const closeSubscriptions: Array<() => void> = []
    const eventSources: EventSource[] = []
    const debounceByRunId: Record<string, ReturnType<typeof setTimeout>> = {}
    let fallbackCheckTimer: ReturnType<typeof setTimeout> | null = null
    let safetyPollTimer: ReturnType<typeof setInterval> | null = null

    const clearRunDebounces = () => {
      for (const t of Object.values(debounceByRunId)) clearTimeout(t)
      for (const k of Object.keys(debounceByRunId)) delete debounceByRunId[k]
    }

    const scheduleDebouncedRefresh = (runId: string) => {
      const existing = debounceByRunId[runId]
      if (existing) clearTimeout(existing)
      debounceByRunId[runId] = setTimeout(() => {
        delete debounceByRunId[runId]
        if (!cancelled) void refreshSingleRun(runId)
      }, POLL_DEBOUNCE_MS)
    }

    const scheduleFallbackIfAllStreamsDead = () => {
      if (fallbackCheckTimer) clearTimeout(fallbackCheckTimer)
      fallbackCheckTimer = setTimeout(() => {
        fallbackCheckTimer = null
        if (cancelled || eventSources.length === 0) return
        const allClosed = eventSources.every((es) => es.readyState === EventSource.CLOSED)
        if (allClosed && !intervalRef.current) {
          clearRunDebounces()
          closeSubscriptions.forEach((c) => c())
          closeSubscriptions.length = 0
          eventSources.length = 0
          if (safetyPollTimer) {
            clearInterval(safetyPollTimer)
            safetyPollTimer = null
          }
          startPolling()
        }
      }, SSE_ALL_CLOSED_CHECK_MS)
    }

    const setup = async () => {
      await poll()
      if (cancelled) return

      for (const doc of docs) {
        const runId = runs[doc]
        if (!runId) continue
        const { close, eventSource } = subscribeToWorkflowEvents(runId, {
          onOpen: () => {
            // Defer: this handler can run before `eventSources.push(eventSource)` in this loop iteration.
            window.setTimeout(() => {
              if (
                cancelled ||
                !fallbackCheckTimer ||
                eventSources.length === 0 ||
                !eventSources.every((es) => es.readyState === EventSource.OPEN)
              ) {
                return
              }
              clearTimeout(fallbackCheckTimer)
              fallbackCheckTimer = null
            }, 0)
          },
          onEvent: (ev) => {
            const wid = typeof ev.workflow_run_id === 'string' ? ev.workflow_run_id : runId
            if (ev.type === 'workflow.failed' || ev.type === 'workflow.completed') {
              void refreshSingleRun(wid)
              return
            }
            scheduleDebouncedRefresh(wid)
          },
          onError: () => {
            scheduleFallbackIfAllStreamsDead()
          },
        })
        closeSubscriptions.push(close)
        eventSources.push(eventSource)
      }

      safetyPollTimer = setInterval(() => {
        if (!cancelled && !intervalRef.current) void poll()
      }, SSE_SAFETY_POLL_MS)
    }

    void setup()

    return () => {
      cancelled = true
      if (fallbackCheckTimer) clearTimeout(fallbackCheckTimer)
      if (safetyPollTimer) clearInterval(safetyPollTimer)
      clearRunDebounces()
      closeSubscriptions.forEach((c) => c())
      stopPolling()
    }
  }, [navigate, status, startPolling, poll, refreshSingleRun])

  useEffect(() => {
    if (status === 'completed' && documents.length === 0) {
      void loadCompletedOutputs().catch(() => {})
    }
  }, [status, documents.length, loadCompletedOutputs])

  const handleViewOutput = () => navigate('/output')

  const docLabels = selectedDocs.length ? selectedDocs : (['PDD', 'SDD', 'UAT'] as DocType[])

  return (
    <div className="min-h-[calc(100vh-56px)] bg-white flex flex-col">
      <div className="bg-ey-nav px-8 py-10">
        <div className="max-w-3xl mx-auto">
          <p className="font-body text-xs tracking-widest uppercase text-ey-primary mb-2 font-medium">
            Pipeline Running
          </p>
          <h1 className="font-display font-bold text-4xl uppercase text-white tracking-tight">
            Generating Documents
          </h1>
        </div>
      </div>

      <div className="flex flex-1 items-center justify-center px-8">
        <div className="w-full max-w-3xl py-20">
          {status === 'failed' ? (
            <div className="animate-fade-in">
              <div className="flex items-start gap-4 border border-red-200 bg-red-50 p-6 mb-8">
                <AlertCircle size={20} color="#DC2626" className="shrink-0 mt-0.5" />
                <div>
                  <p className="font-body font-semibold text-red-700 text-sm mb-1">
                    Generation Failed
                  </p>
                  <p className="font-body text-sm text-red-600">
                    {errorMessage ?? 'An unexpected error occurred. Please check your backend.'}
                  </p>
                </div>
              </div>
              <button
                type="button"
                onClick={() => navigate('/')}
                className="flex items-center gap-3 px-8 py-4 bg-ey-ink-strong text-ey-primary font-display font-bold uppercase tracking-widest hover:bg-ey-ink transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-ey-primary focus-visible:ring-offset-2"
              >
                <RefreshCw size={16} className="shrink-0" />
                Try Again
              </button>
            </div>
          ) : (
            <>
              <div className="flex flex-wrap items-center gap-6 mb-12 animate-fade-in">
                {docLabels.map((doc) => {
                  const done = status === 'completed'
                  const tp = perTypeProgress[doc]
                  return (
                    <div key={doc} className="flex items-center gap-2">
                      <div
                        className={`w-2 h-2 rounded-full transition-colors duration-500 ${
                          done ? 'bg-ey-primary' : 'bg-ey-border animate-pulse'
                        }`}
                      />
                      <span className="font-display font-bold text-lg uppercase text-ey-ink-strong tracking-wide">
                        {doc}
                      </span>
                      {tp !== undefined && status === 'running' && (
                        <span className="font-body text-xs text-ey-muted">{tp}%</span>
                      )}
                    </div>
                  )
                })}
              </div>

              <ProgressBar />

              {status === 'running' && (
                <div className="mt-4 space-y-1 font-body text-xs text-ey-muted max-h-24 overflow-y-auto">
                  {selectedDocs.map((doc) =>
                    perTypeStep[doc] ? (
                      <p key={doc}>
                        <span className="font-semibold text-ey-ink-strong">{doc}:</span> {perTypeStep[doc]}
                      </p>
                    ) : null
                  )}
                </div>
              )}

              {status === 'running' && progress < 100 && (
                <p className="font-body text-xs text-ey-muted mt-6 animate-fade-in">
                  {currentStep || 'This may take a few minutes depending on document length.'}
                </p>
              )}

              {status === 'completed' && (
                <div className="mt-12 animate-slide-up">
                  <div className="flex items-center gap-3 mb-6">
                    <div className="w-6 h-6 bg-ey-primary text-ey-ink-strong flex items-center justify-center">
                      <svg width="12" height="10" viewBox="0 0 12 10" fill="none" aria-hidden="true">
                        <path
                          d="M1 5L4.5 8.5L11 1"
                          stroke="currentColor"
                          strokeWidth="2"
                          strokeLinecap="square"
                        />
                      </svg>
                    </div>
                    <span className="font-display font-bold text-xl uppercase tracking-wide text-ey-ink-strong">
                      {documents.length} Document{documents.length !== 1 ? 's' : ''} Ready
                    </span>
                  </div>
                  <button
                    type="button"
                    onClick={handleViewOutput}
                    className="group flex items-center gap-4 px-10 py-5 bg-ey-ink-strong text-ey-primary font-display font-bold text-xl uppercase tracking-widest hover:bg-ey-primary hover:text-ey-ink-strong transition-all focus:outline-none focus-visible:ring-2 focus-visible:ring-ey-primary focus-visible:ring-offset-2"
                  >
                    View &amp; Download
                    <ArrowRight size={20} className="transition-transform group-hover:translate-x-1 text-current" />
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  )
}
