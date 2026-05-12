/**
 * Upload page (route: `/`).
 *
 * Lets the user:
 *
 * 1. Upload a BRD file (PDF / DOCX) via {@link FileUploader}.
 * 2. Choose which deliverables (PDD / SDD / UAT) to generate via
 *    {@link DocumentSelector}.
 * 3. Pick a template per selected deliverable via {@link TemplateSelector}.
 * 4. Submit — the page calls `uploadDocument` then `createWorkflow` for
 *    every chosen deliverable in parallel, stores the run ids in the job
 *    store, and navigates to `/progress`.
 *
 * Validation runs inline (no toasts) so the user sees the exact reason a
 * submission was rejected next to the offending control.
 */
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowRight, AlertCircle } from 'lucide-react'
import { FileUploader } from '../components/upload/FileUploader'
import { DocumentSelector } from '../components/upload/DocumentSelector'
import { TemplateSelector } from '../components/upload/TemplateSelector'
import { useJobStore, type DocType } from '../store/useJobStore'
import { uploadDocument } from '../api/documentApi'
import { createWorkflow } from '../api/workflowApi'
import { getApiErrorMessage } from '../api/errors'

export function UploadPage() {
  const navigate = useNavigate()
  const {
    uploadedFile,
    selectedDocs,
    selectedTemplateByType,
    setDocumentId,
    setWorkflowRuns,
    setStatus,
    setError,
  } = useJobStore()

  const [submitting, setSubmitting] = useState(false)
  const [validationError, setValidationError] = useState<string | null>(null)

  const templatesReady = selectedDocs.every(
    (d) => Boolean(selectedTemplateByType[d])
  )
  const canSubmit = Boolean(uploadedFile) && selectedDocs.length > 0 && templatesReady

  const handleGenerate = async () => {
    if (!uploadedFile) {
      setValidationError('Please upload a BRD or DOCX file.')
      return
    }
    if (selectedDocs.length === 0) {
      setValidationError('Select at least one document type.')
      return
    }
    const missing = selectedDocs.filter((d) => !selectedTemplateByType[d])
    if (missing.length > 0) {
      setValidationError(
        `Select a template for each output type (missing: ${missing.join(', ')}).`
      )
      return
    }
    setValidationError(null)

    const runs: Partial<Record<DocType, string>> = {}

    try {
      setSubmitting(true)
      setError(null)

      const docRes = await uploadDocument(uploadedFile)
      const document_id = docRes.document_id
      setDocumentId(document_id)

      // Serialize workflow creation to reduce concurrent ingestion on the same document_id.
      for (const doc of selectedDocs) {
        const template_id = selectedTemplateByType[doc]!
        try {
          const created = await createWorkflow({
            document_id,
            template_id,
            start_immediately: true,
          })
          runs[doc] = created.workflow_run_id
        } catch (workflowErr: unknown) {
          const msg = getApiErrorMessage(
            workflowErr,
            'Failed to create workflow run.'
          )
          setWorkflowRuns({ ...runs })
          const detail = `Failed while starting ${doc} (template ${template_id}): ${msg}`
          setError(detail)
          setValidationError(detail)
          setStatus(Object.keys(runs).length ? 'running' : 'idle')
          return
        }
      }

      setWorkflowRuns(runs)
      setStatus('running')

      navigate('/progress')
    } catch (err: unknown) {
      const msg = getApiErrorMessage(err, 'Failed to start pipeline. Check your backend.')
      setError(msg)
      setValidationError(msg)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="min-h-[calc(100vh-56px)] bg-white">
      <div className="bg-ey-nav text-white px-8 py-12">
        <div className="max-w-5xl mx-auto">
          <div className="flex items-start gap-4 mb-6">
            <div className="w-1 h-12 bg-ey-primary shrink-0" />
            <div>
              <p className="font-body text-xs tracking-widest uppercase text-ey-primary mb-1 font-medium">
                AI SDLC Platform
              </p>
              <h1 className="font-display font-bold text-5xl uppercase leading-none tracking-tight text-white">
                Document<br />Generator
              </h1>
            </div>
          </div>
          <p className="font-body text-sm text-white/50 max-w-lg leading-relaxed">
            Upload your Business Requirements Document and let the pipeline generate
            enterprise-grade PDD, SDD, and UAT documentation automatically.
          </p>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-8 py-12">
        <div className="space-y-12">
          <section className="animate-slide-up">
            <SectionLabel number="01" label="Upload Document" />
            <FileUploader />
          </section>

          <section className="animate-slide-up" style={{ animationDelay: '0.1s' }}>
            <SectionLabel number="02" label="Output Documents" />
            <DocumentSelector />
          </section>

          <section className="animate-slide-up" style={{ animationDelay: '0.15s' }}>
            <SectionLabel number="03" label="Templates (one per type)" />
            <TemplateSelector />
          </section>

          {validationError && (
            <div className="flex items-center gap-3 border border-red-200 bg-red-50 px-5 py-4 animate-fade-in">
              <AlertCircle size={16} color="#DC2626" />
              <p className="font-body text-sm text-red-600">{validationError}</p>
            </div>
          )}

          <div className="pt-2 animate-slide-up" style={{ animationDelay: '0.2s' }}>
            <button
              type="button"
              onClick={handleGenerate}
              disabled={submitting}
              className={`group flex items-center gap-4 px-10 py-5 font-display font-bold text-xl uppercase tracking-widest transition-all focus:outline-none focus-visible:ring-2 focus-visible:ring-ey-primary focus-visible:ring-offset-2 ${
                submitting
                  ? 'bg-ey-border text-ey-muted cursor-not-allowed'
                  : canSubmit
                    ? 'bg-ey-ink-strong text-ey-primary hover:bg-ey-primary hover:text-ey-ink-strong'
                    : 'bg-ey-surface text-ey-muted hover:bg-ey-border'
              }`}
            >
              {submitting ? 'Starting Pipeline…' : 'Generate Documents'}
              {!submitting && (
                <ArrowRight
                  size={20}
                  className="transition-transform group-hover:translate-x-1 text-current"
                />
              )}
            </button>

            <div className="flex items-center gap-6 mt-5 flex-wrap">
              <StatusDot active={!!uploadedFile} label="File ready" />
              <StatusDot
                active={selectedDocs.length > 0}
                label={`${selectedDocs.length} doc(s) selected`}
              />
              <StatusDot active={templatesReady} label="Templates for each type" />
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function SectionLabel({ number, label }: { number: string; label: string }) {
  return (
    <div className="flex items-center gap-3 mb-5">
      <span className="font-display font-bold text-3xl text-ey-primary leading-none">{number}</span>
      <div className="h-px flex-1 bg-ey-border" />
      <span className="font-body text-xs font-semibold tracking-widest uppercase text-ey-muted">
        {label}
      </span>
    </div>
  )
}

function StatusDot({ active, label }: { active: boolean; label: string }) {
  return (
    <div className="flex items-center gap-2">
      <div
        className={`w-2 h-2 rounded-full transition-colors ${active ? 'bg-ey-ink-strong' : 'bg-ey-border'}`}
      />
      <span
        className={`font-body text-xs transition-colors ${active ? 'text-ey-ink-strong font-medium' : 'text-ey-muted'}`}
      >
        {label}
      </span>
    </div>
  )
}
