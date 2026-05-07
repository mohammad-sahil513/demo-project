import { useState } from 'react'
import { ChevronDown, ChevronRight } from 'lucide-react'
import type { CitationDto } from '../../api/types'

const CHUNK_ID_MAX = 36

function truncateChunkId(id: string): string {
  const t = id.trim()
  if (!t) return ''
  if (t.length <= CHUNK_ID_MAX) return t
  return `${t.slice(0, CHUNK_ID_MAX)}…`
}

function CitationRow({ c }: { c: CitationDto }) {
  const page = c.page == null ? '?' : String(c.page)
  const kind = c.content_type ?? 'text'
  const section = c.path?.trim() || '—'
  const idLine = truncateChunkId(c.chunk_id)

  return (
    <div
      className="font-body text-[11px] leading-snug text-ey-ink border-b border-ey-border/60 pb-3 last:border-0 last:pb-0 space-y-1"
    >
      <div className="grid grid-cols-[1fr_auto_auto] gap-x-2 gap-y-0.5 items-start">
        <span className="text-ey-ink-strong min-w-0 break-words" title={section}>
          {section}
        </span>
        <span className="text-ey-muted shrink-0 tabular-nums">p.{page}</span>
        <span className="text-ey-muted shrink-0 uppercase text-[10px] tracking-wide">{kind}</span>
      </div>
      {idLine ? (
        <p className="text-[10px] text-ey-muted/90 font-mono truncate" title={c.chunk_id}>
          id: {idLine}
        </p>
      ) : null}
    </div>
  )
}

export function CitationPanel({ citations }: { citations: CitationDto[] }) {
  const [open, setOpen] = useState(true)

  return (
    <div className="border-l border-ey-border bg-white shrink-0 w-72 flex flex-col max-h-full">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="flex items-center gap-2 px-5 py-4 border-b border-ey-border text-left w-full hover:bg-ey-surface/50 transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-ey-primary"
        aria-expanded={open}
      >
        {open ? <ChevronDown size={14} className="text-ey-muted shrink-0" /> : <ChevronRight size={14} className="text-ey-muted shrink-0" />}
        <div className="min-w-0">
          <p className="font-body text-[10px] tracking-widest uppercase text-ey-muted font-medium">
            Citations
          </p>
          <p className="font-body text-xs text-ey-ink-strong mt-0.5">
            {citations.length} source{citations.length !== 1 ? 's' : ''}
          </p>
        </div>
      </button>
      {open && (
        <div className="flex-1 overflow-y-auto px-5 py-4 space-y-3">
          {citations.length === 0 ? (
            <p className="font-body text-xs text-ey-muted">No citations for this section.</p>
          ) : (
            <>
              <p className="font-body text-[9px] tracking-widest uppercase text-ey-muted font-semibold">
                Section / Page / Type
              </p>
              <p className="font-body text-[10px] text-ey-muted leading-tight -mt-1">
                Section is the source chunk heading from retrieval, not a file path.
              </p>
              {citations.map((c, index) => (
                <CitationRow
                  key={`${c.chunk_id || 'no-id'}-${index}`}
                  c={c}
                />
              ))}
            </>
          )}
        </div>
      )}
    </div>
  )
}
