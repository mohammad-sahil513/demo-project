import { useRef, useState, DragEvent, ChangeEvent } from 'react'
import { Upload, X, FileText, Plus, Check } from 'lucide-react'
import { templateApi } from '../../api/templateApi'
import { getApiErrorMessage } from '../../api/errors'

const DOC_TYPES = ['PDD', 'SDD', 'UAT'] as const
type DocType = typeof DOC_TYPES[number]

interface Props {
  onSuccess: () => void
}

export function AddTemplatePanel({ onSuccess }: Props) {
  const [selectedType, setSelectedType] = useState<DocType | null>(null)
  const [file, setFile] = useState<File | null>(null)
  const [isDragging, setIsDragging] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)
  const fileRef = useRef<HTMLInputElement>(null)

  const allowedExtension = selectedType === 'UAT' ? 'xlsx' : 'docx'
  const allowedLabel = allowedExtension.toUpperCase()

  const handleFile = (f: File) => {
    const ext = f.name.split('.').pop()?.toLowerCase()
    if (ext !== allowedExtension) {
      setError(`Only ${allowedLabel} files are accepted for ${selectedType ?? 'selected'} templates.`)
      return
    }
    setError(null)
    setFile(f)
  }

  const onDrop = (e: DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    const f = e.dataTransfer.files[0]
    if (f) handleFile(f)
  }

  const canSubmit = selectedType && file && !uploading

  const handleSubmit = async () => {
    if (!canSubmit) {
      if (!selectedType) setError('Select a document type first.')
      else if (!file) setError(`Upload a ${allowedLabel} template file.`)
      return
    }
    setError(null)
    setUploading(true)
    try {
      await templateApi.uploadTemplate({
        file,
        template_type: selectedType,
      })
      setSuccess(true)
      setTimeout(() => {
        setSuccess(false)
        setFile(null)
        setSelectedType(null)
        onSuccess()
      }, 1500)
    } catch (err: unknown) {
      setError(getApiErrorMessage(err, 'Upload failed. Check backend logs.'))
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="border border-ey-border bg-white">
      <div className="flex items-center gap-3 px-6 py-4 border-b border-ey-border bg-ey-surface/80">
        <div className="w-6 h-6 bg-ey-ink-strong text-ey-primary flex items-center justify-center shrink-0">
          <Plus size={13} className="text-current" />
        </div>
        <h3 className="font-display font-bold text-lg uppercase tracking-wide text-ey-ink-strong">
          Add New Template
        </h3>
      </div>

      <div className="p-6 space-y-6">
        <div>
          <label className="font-body text-[10px] tracking-widest uppercase text-ey-muted font-medium block mb-3">
            Document Type
          </label>
          <div className="flex gap-3">
            {DOC_TYPES.map((type) => {
              const active = selectedType === type
              return (
                <button
                  key={type}
                  type="button"
                  onClick={() => setSelectedType(type)}
                  className={`flex-1 py-3 border-2 font-display font-bold text-xl uppercase tracking-widest transition-all focus:outline-none focus-visible:ring-2 focus-visible:ring-ey-primary focus-visible:ring-offset-2 ${
                    active
                      ? 'border-ey-ink-strong bg-ey-ink-strong text-ey-primary'
                      : 'border-ey-border bg-white text-ey-ink-strong hover:border-ey-ink-strong'
                  }`}
                >
                  {type}
                </button>
              )
            })}
          </div>
        </div>

        <div>
          <label className="font-body text-[10px] tracking-widest uppercase text-ey-muted font-medium block mb-2">
            Template File ({allowedLabel})
          </label>
          {selectedType === 'UAT' && (
            <p className="font-body text-xs text-ey-muted mb-2">
              Use row-1 headers in each sheet. These headers are used as schema for UAT export validation.
            </p>
          )}

          {file ? (
            <div className="border border-ey-border px-4 py-3 flex items-center gap-3 animate-fade-in">
              <FileText size={18} className="text-ey-muted shrink-0" />
              <span className="font-body text-sm text-ey-ink-strong flex-1 truncate">{file.name}</span>
              <span className="font-body text-xs text-ey-muted">{(file.size / 1024).toFixed(0)} KB</span>
              <button
                type="button"
                onClick={() => setFile(null)}
                className="shrink-0 hover:bg-ey-canvas p-1 transition-colors text-ey-muted hover:text-ey-ink-strong"
              >
                <X size={14} />
              </button>
            </div>
          ) : (
            <div
              onDrop={onDrop}
              onDragOver={(e) => {
                e.preventDefault()
                setIsDragging(true)
              }}
              onDragLeave={() => setIsDragging(false)}
              onClick={() => fileRef.current?.click()}
              className={`border-2 border-dashed cursor-pointer p-8 flex flex-col items-center gap-3 transition-all ${
                isDragging
                  ? 'border-ey-primary bg-ey-primary/10'
                  : 'border-ey-border bg-ey-surface hover:border-ey-ink-strong hover:bg-white'
              }`}
            >
              <Upload size={20} className={isDragging ? 'text-ey-ink-strong' : 'text-ey-muted'} />
              <p className="font-body text-sm text-ey-muted text-center">
                Drop {allowedLabel} here or <span className="text-ey-ink-strong font-medium underline">browse</span>
              </p>
            </div>
          )}
          <input
            ref={fileRef}
            type="file"
            accept={allowedExtension === 'xlsx' ? '.xlsx' : '.docx'}
            className="hidden"
            onChange={(e: ChangeEvent<HTMLInputElement>) => {
              const f = e.target.files?.[0]
              if (f) handleFile(f)
              e.target.value = ''
            }}
          />
        </div>

        {error && <p className="font-body text-xs text-red-500 animate-fade-in">{error}</p>}

        <div className="flex items-center justify-between pt-1">
          <div className="flex items-center gap-4">
            <Dot active={!!selectedType} label="Type" />
            <Dot active={!!file} label="File" />
          </div>

          <button
            type="button"
            onClick={handleSubmit}
            disabled={!canSubmit || success}
            className={`flex items-center gap-2 px-6 py-3 font-display font-bold text-sm uppercase tracking-widest transition-all focus:outline-none focus-visible:ring-2 focus-visible:ring-ey-primary focus-visible:ring-offset-2 ${
              success
                ? 'bg-ey-primary text-ey-ink-strong'
                : canSubmit
                  ? 'bg-ey-ink-strong text-ey-primary hover:bg-ey-ink'
                  : 'bg-ey-canvas text-ey-muted cursor-not-allowed'
            }`}
          >
            {success ? (
              <>
                <Check size={14} strokeWidth={3} />
                Uploaded
              </>
            ) : uploading ? (
              'Uploading…'
            ) : (
              'Upload Template'
            )}
          </button>
        </div>
      </div>
    </div>
  )
}

function Dot({ active, label }: { active: boolean; label: string }) {
  return (
    <div className="flex items-center gap-1.5">
      <div
        className={`w-1.5 h-1.5 rounded-full transition-colors ${active ? 'bg-ey-ink-strong' : 'bg-ey-border'}`}
      />
      <span
        className={`font-body text-xs transition-colors ${active ? 'text-ey-ink-strong font-medium' : 'text-ey-muted'}`}
      >
        {label}
      </span>
    </div>
  )
}
