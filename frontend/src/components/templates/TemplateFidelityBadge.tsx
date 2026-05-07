interface Props {
  validationStatus?: string | null
}

export function TemplateFidelityBadge({ validationStatus }: Props) {
  const status = (validationStatus || 'unknown').toLowerCase()
  const style =
    status === 'valid'
      ? 'bg-green-100 text-green-700'
      : status === 'invalid'
        ? 'bg-red-100 text-red-700'
        : status === 'warning'
          ? 'bg-amber-100 text-amber-700'
          : 'bg-ey-canvas text-ey-muted'
  const label =
    status === 'valid'
      ? 'Fidelity Valid'
      : status === 'invalid'
        ? 'Fidelity Invalid'
        : status === 'warning'
          ? 'Fidelity Warning'
          : 'Fidelity Unknown'
  return <span className={`font-body text-[9px] font-semibold tracking-widest uppercase px-2 py-0.5 ${style}`}>{label}</span>
}

