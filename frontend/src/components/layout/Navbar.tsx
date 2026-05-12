/**
 * Top navigation bar — persistent across every route.
 *
 * Renders three job-flow steps (Upload, Generate, Review) as buttons
 * with progressive enablement: a step becomes clickable only after the
 * previous step's job state allows it (e.g. "Review" enables once
 * `status === 'completed'`). A separate "Templates" button always
 * routes to `/templates` regardless of job state.
 *
 * Clicking the logo resets the job store and returns to `/`.
 */
import { useNavigate, useLocation } from 'react-router-dom'
import clsx from 'clsx'
import { useJobStore } from '../../store/useJobStore'

const navBtnFocus =
  'focus:outline-none focus-visible:ring-2 focus-visible:ring-ey-primary focus-visible:ring-offset-2 focus-visible:ring-offset-ey-nav'

export function Navbar() {
  const navigate = useNavigate()
  const location = useLocation()
  const { status, workflowRunByType, reset } = useJobStore()

  const hasWorkflowRuns = Object.values(workflowRunByType).some(Boolean)

  const jobSteps = [
    { label: 'Upload', path: '/' },
    { label: 'Generate', path: '/progress' },
    { label: 'Review', path: '/output' },
  ]

  const handleLogo = () => {
    reset()
    navigate('/')
  }

  const isTemplatesPage = location.pathname.startsWith('/templates')

  return (
    <nav
      className="bg-ey-nav text-white h-14 flex items-center px-6 sm:px-8 sticky top-0 z-50 gap-4 sm:gap-6 border-b border-white/10"
      aria-label="Primary"
    >
      <button
        type="button"
        onClick={handleLogo}
        className={clsx('flex items-center gap-3 group mr-auto shrink-0 min-w-0', navBtnFocus, 'rounded-sm')}
      >
        <img
          src="/brand/ey-logo.svg"
          alt="AI SDLC"
          width={132}
          height={28}
          className="h-7 w-auto block"
        />
        <span className="font-body font-semibold text-sm tracking-wide text-white/90 hidden lg:inline">
          Document Generator
        </span>
      </button>

      <div className="flex items-center gap-3 sm:gap-4 min-w-0">
        <button
          type="button"
          onClick={() => navigate('/templates')}
          className={clsx(
            navBtnFocus,
            'rounded-sm px-3 py-1.5 font-body text-[11px] font-semibold uppercase tracking-widest transition-colors border',
            isTemplatesPage
              ? 'text-ey-ink-strong bg-ey-primary border-ey-primary'
              : 'text-white/70 border-white/20 hover:text-white hover:border-white/40 bg-transparent'
          )}
        >
          Templates
        </button>

        <div className="hidden sm:block w-px h-6 bg-white/15 shrink-0" aria-hidden="true" />

        <div className="flex items-center gap-1 sm:gap-2 min-w-0 overflow-x-auto py-1 [scrollbar-width:none] [-ms-overflow-style:none] [&::-webkit-scrollbar]:hidden">
          {jobSteps.map((step, i) => {
            const active = location.pathname === step.path && !isTemplatesPage
            const isAccessible =
              step.path === '/' ||
              (step.path === '/progress' &&
                hasWorkflowRuns &&
                ['running', 'completed', 'failed'].includes(status)) ||
              (step.path === '/output' && status === 'completed')

            return (
              <button
                key={i}
                type="button"
                onClick={() => isAccessible && navigate(step.path)}
                disabled={!isAccessible}
                className={clsx(
                  navBtnFocus,
                  'shrink-0 rounded-sm px-2.5 sm:px-3 py-1.5 font-body text-[11px] sm:text-xs font-medium tracking-wide transition-colors',
                  active
                    ? 'text-ey-primary underline decoration-2 underline-offset-4'
                    : isAccessible
                      ? 'text-white/60 hover:text-white'
                      : 'text-white/25 cursor-not-allowed'
                )}
              >
                {step.label}
              </button>
            )
          })}
        </div>
      </div>
    </nav>
  )
}
