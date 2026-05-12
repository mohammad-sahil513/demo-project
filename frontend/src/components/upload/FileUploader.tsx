/**
 * BRD file upload card — drag-and-drop area + file picker fallback.
 *
 * Accepts only `.pdf` and `.docx`. The selected file is stored on the
 * job store as a {@link File}; the actual upload to the backend happens
 * when the user submits the upload page form. This keeps the network
 * round-trip out of the on-drop handler so the UI stays snappy.
 */
import { useRef, useState, DragEvent, ChangeEvent } from 'react'
import { Upload, File, X } from 'lucide-react'
import { useJobStore } from '../../store/useJobStore'

export function FileUploader() {
  const { uploadedFile, setUploadedFile } = useJobStore()
  const [isDragging, setIsDragging] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  const handleFile = (file: File) => {
    const ext = file.name.split('.').pop()?.toLowerCase()
    if (ext === 'pdf' || ext === 'docx') {
      setUploadedFile(file)
    } else {
      alert('Only PDF and DOCX files are supported.')
    }
  }

  const onDrop = (e: DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    const file = e.dataTransfer.files[0]
    if (file) handleFile(file)
  }

  const onDragOver = (e: DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const onDragLeave = () => setIsDragging(false)

  const onChange = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) handleFile(file)
  }

  const formatSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  if (uploadedFile) {
    return (
      <div className="border border-ey-border bg-white p-4 flex items-center gap-4 animate-fade-in">
        <div className="w-10 h-10 bg-ey-ink-strong text-ey-primary flex items-center justify-center shrink-0">
          <File size={18} className="text-current" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="font-body font-medium text-sm text-ey-ink-strong truncate">{uploadedFile.name}</p>
          <p className="font-body text-xs text-ey-muted mt-0.5">{formatSize(uploadedFile.size)}</p>
        </div>
        <button
          type="button"
          onClick={() => setUploadedFile(null)}
          className="w-8 h-8 flex items-center justify-center hover:bg-ey-surface transition-colors shrink-0 text-ey-muted hover:text-ey-ink-strong"
        >
          <X size={16} />
        </button>
      </div>
    )
  }

  return (
    <div
      onDrop={onDrop}
      onDragOver={onDragOver}
      onDragLeave={onDragLeave}
      onClick={() => inputRef.current?.click()}
      className={`border-2 border-dashed transition-all cursor-pointer p-10 flex flex-col items-center gap-4
        ${isDragging
          ? 'border-ey-primary bg-ey-primary/10'
          : 'border-ey-border bg-ey-surface hover:border-ey-ink-strong hover:bg-white'
        }`}
    >
      <div
        className={`w-12 h-12 flex items-center justify-center transition-colors ${
          isDragging ? 'bg-ey-primary text-ey-ink-strong' : 'bg-ey-ink-strong text-ey-primary'
        }`}
      >
        <Upload size={22} className="text-current" />
      </div>
      <div className="text-center">
        <p className="font-display font-bold text-xl uppercase tracking-wide text-ey-ink-strong">
          Drop your BRD here
        </p>
        <p className="font-body text-sm text-ey-muted mt-1">
          or <span className="text-ey-ink-strong font-medium underline">browse files</span> — PDF or DOCX accepted
        </p>
      </div>
      <input
        ref={inputRef}
        type="file"
        accept=".pdf,.docx"
        onChange={onChange}
        className="hidden"
      />
    </div>
  )
}
