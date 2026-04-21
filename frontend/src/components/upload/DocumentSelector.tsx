import { useJobStore, DocType } from '../../store/useJobStore'

const DOC_OPTIONS: { type: DocType; label: string; desc: string }[] = [
  { type: 'PDD', label: 'PDD', desc: 'Product Design Document' },
  { type: 'SDD', label: 'SDD', desc: 'System Design Document' },
  { type: 'UAT', label: 'UAT', desc: 'User Acceptance Testing' },
]

export function DocumentSelector() {
  const { selectedDocs, toggleDoc, setSelectedDocs } = useJobStore()

  const allSelected = selectedDocs.length === DOC_OPTIONS.length

  return (
    <div>
      <div className="flex items-center justify-between mb-3">
        <p className="font-body text-xs font-medium tracking-widest text-ey-muted uppercase">
          Documents to Generate
        </p>
        <button
          type="button"
          onClick={() =>
            allSelected
              ? setSelectedDocs([])
              : setSelectedDocs(DOC_OPTIONS.map((d) => d.type))
          }
          className="font-body text-xs text-ey-ink-strong underline focus:outline-none focus-visible:ring-2 focus-visible:ring-ey-primary rounded-sm"
        >
          {allSelected ? 'Deselect all' : 'Select all'}
        </button>
      </div>
      <div className="grid grid-cols-3 gap-3">
        {DOC_OPTIONS.map(({ type, label, desc }) => {
          const checked = selectedDocs.includes(type)
          return (
            <button
              key={type}
              type="button"
              onClick={() => toggleDoc(type)}
              className={`p-4 border-2 text-left transition-all focus:outline-none focus-visible:ring-2 focus-visible:ring-ey-primary focus-visible:ring-offset-2 ${
                checked
                  ? 'border-ey-ink-strong bg-ey-ink-strong text-white'
                  : 'border-ey-border bg-white text-ey-ink-strong hover:border-ey-ink-strong'
              }`}
            >
              <div className="flex items-start justify-between gap-2 mb-2">
                <span
                  className={`font-display font-bold text-2xl tracking-wide ${
                    checked ? 'text-ey-primary' : 'text-ey-ink-strong'
                  }`}
                >
                  {label}
                </span>
                <div
                  className={`w-5 h-5 border-2 flex items-center justify-center shrink-0 mt-1 transition-colors ${
                    checked ? 'border-ey-primary bg-ey-primary text-ey-ink-strong' : 'border-ey-border bg-white'
                  }`}
                >
                  {checked && (
                    <svg width="10" height="8" viewBox="0 0 10 8" fill="none" aria-hidden="true">
                      <path
                        d="M1 4L3.5 6.5L9 1"
                        stroke="currentColor"
                        strokeWidth="1.8"
                        strokeLinecap="square"
                      />
                    </svg>
                  )}
                </div>
              </div>
              <p className={`font-body text-xs ${checked ? 'text-white/70' : 'text-ey-muted'}`}>
                {desc}
              </p>
            </button>
          )
        })}
      </div>
    </div>
  )
}
