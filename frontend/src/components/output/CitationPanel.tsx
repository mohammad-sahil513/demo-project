import { useState } from 'react'
import { ChevronDown, ChevronRight } from 'lucide-react'
import type { CitationDto } from '../../api/types'

function formatLine(c: CitationDto): string {
  const page = c.page == null ? '?' : String(c.page)
  const kind = c.content_type ?? 'text'
  return `${c.path}, p.${page} [${kind}]`
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
            citations.map((c) => (
              <p
                key={c.chunk_id}
                className="font-body text-[11px] leading-snug text-ey-ink border-b border-ey-border/60 pb-3 last:border-0 last:pb-0"
              >
                {formatLine(c)}
              </p>
            ))
          )}
        </div>
      )}
    </div>
  )
}
