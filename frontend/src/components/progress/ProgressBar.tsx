/**
 * Circular segmented progress indicator used on the Progress page.
 *
 * Draws {@link SEGMENTS} pie slices around a circle; the number of
 * filled slices is derived from the workflow's `overall_progress_percent`
 * (0-100). The center shows the current phase label and a percentage.
 *
 * Pure visual component — it reads the active workflow status from
 * {@link useJobStore} so callers do not have to thread props through.
 */
import { useJobStore } from '../../store/useJobStore'

const SEGMENTS = 12
const PAD = 1.35
const SLOT = 360 / SEGMENTS

function segmentPath(
  cx: number,
  cy: number,
  rOuter: number,
  rInner: number,
  index: number
): string {
  const startDeg = -90 + index * SLOT + PAD
  const endDeg = -90 + (index + 1) * SLOT - PAD
  const rad = (d: number) => (d * Math.PI) / 180
  const pt = (r: number, deg: number) => ({
    x: cx + r * Math.cos(rad(deg)),
    y: cy + r * Math.sin(rad(deg)),
  })
  const o1 = pt(rOuter, startDeg)
  const o2 = pt(rOuter, endDeg)
  const i2 = pt(rInner, endDeg)
  const i1 = pt(rInner, startDeg)
  const sweep = endDeg - startDeg
  const large = sweep > 180 ? 1 : 0
  return [
    `M ${o1.x} ${o1.y}`,
    `A ${rOuter} ${rOuter} 0 ${large} 1 ${o2.x} ${o2.y}`,
    `L ${i2.x} ${i2.y}`,
    `A ${rInner} ${rInner} 0 ${large} 0 ${i1.x} ${i1.y}`,
    'Z',
  ].join(' ')
}

export function ProgressBar() {
  const { progress, currentStep, status } = useJobStore()

  const isFailed = status === 'failed'
  const isComplete = status === 'completed'

  const filledCount = Math.min(
    SEGMENTS,
    Math.max(0, Math.round((progress / 100) * SEGMENTS))
  )

  const cx = 60
  const cy = 60
  const rOuter = 52
  const rInner = 38

  return (
    <div className="w-full animate-fade-in">
      <div className="flex justify-center py-2">
        <div className="relative w-44 h-44 sm:w-52 sm:h-52 shrink-0">
          <svg
            viewBox="0 0 120 120"
            className="h-full w-full"
            role="progressbar"
            aria-valuemin={0}
            aria-valuemax={100}
            aria-valuenow={progress}
            aria-label={`Pipeline progress ${progress} percent`}
          >
            {Array.from({ length: SEGMENTS }, (_, i) => {
              const on = i < filledCount
              let fill: string
              if (isFailed) {
                fill = on ? '#EF4444' : '#E8E8E8'
              } else {
                fill = on ? '#FFE600' : '#E8E8E8'
              }
              return (
                <path
                  key={i}
                  d={segmentPath(cx, cy, rOuter, rInner, i)}
                  fill={fill}
                  className="transition-[fill] duration-500 ease-out"
                />
              )
            })}
          </svg>
          <div className="pointer-events-none absolute inset-0 flex items-center justify-center">
            <span
              className={`font-display text-2xl sm:text-3xl font-bold tracking-tight tabular-nums ${
                isFailed ? 'text-red-500' : 'text-ey-ink-strong'
              }`}
            >
              {progress}
              <span className="text-ey-primary">%</span>
            </span>
          </div>
        </div>
      </div>

      <p className="font-body text-sm text-ey-muted text-center mt-4 max-w-xl mx-auto">
        {isFailed
          ? 'Generation failed'
          : isComplete
            ? 'All documents ready'
            : currentStep || 'Initialising pipeline…'}
      </p>
    </div>
  )
}
