/**
 * Tests for `subscribeToWorkflowEvents`.
 *
 * The mock `EventSource` lets us simulate `onopen`/`onmessage`/`onerror`
 * lifecycles without a real backend so the test can assert handler
 * invocation, JSON parsing tolerance, and proper teardown on `close()`.
 */
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { subscribeToWorkflowEvents } from './workflowApi'

describe('subscribeToWorkflowEvents', () => {
  beforeEach(() => {
    vi.stubGlobal(
      'EventSource',
      class MockEventSource {
        static readonly CONNECTING = 0
        static readonly OPEN = 1
        static readonly CLOSED = 2
        url: string
        readyState: number = MockEventSource.CONNECTING
        onopen: (() => void) | null = null
        onmessage: ((e: MessageEvent) => void) | null = null
        onerror: ((e: Event) => void) | null = null

        constructor(url: string) {
          this.url = url
          queueMicrotask(() => {
            this.readyState = MockEventSource.OPEN
            this.onopen?.()
          })
        }

        close() {
          this.readyState = MockEventSource.CLOSED
        }
      }
    )
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('builds stream URL and forwards parsed events', async () => {
    const seen: string[] = []
    const { close, eventSource } = subscribeToWorkflowEvents('wf-abc', {
      onEvent: (e) => seen.push(e.type),
    })

    await new Promise<void>((r) => queueMicrotask(r))

    expect(eventSource.url).toContain('/workflow-runs/wf-abc/events')
    eventSource.onmessage?.({
      data: JSON.stringify({ type: 'phase.started', workflow_run_id: 'wf-abc', phase: 'INGESTION' }),
    } as MessageEvent)

    expect(seen).toEqual(['phase.started'])
    close()
    expect(eventSource.readyState).toBe(2)
  })
})
