/**
 * Workflow API — create runs, poll status, subscribe to SSE.
 *
 * `subscribeToWorkflowEvents` opens an `EventSource` against the backend
 * `/workflow-runs/{id}/events` stream. The browser handles reconnects,
 * but we still expose `close()` so callers can tear down the stream on
 * unmount (and prevent terminal events from being processed twice).
 *
 * Non-JSON payloads (server heartbeats) are silently ignored — the
 * backend emits them as comment lines, but some intermediaries reshape
 * them into empty data messages.
 */
import client, { baseURL } from './client'
import type { WorkflowCreateData, WorkflowStatusData } from './types'

export interface WorkflowSseEvent {
  type: string
  workflow_run_id: string
  timestamp?: string
  [key: string]: unknown
}

export interface SubscribeWorkflowEventsHandlers {
  onEvent?: (event: WorkflowSseEvent) => void
  onOpen?: () => void
  onError?: (ev: Event) => void
}

export function subscribeToWorkflowEvents(
  workflowRunId: string,
  handlers: SubscribeWorkflowEventsHandlers = {}
): { close: () => void; eventSource: EventSource } {
  const url = `${baseURL}/workflow-runs/${encodeURIComponent(workflowRunId)}/events`
  const es = new EventSource(url)

  es.onopen = () => handlers.onOpen?.()

  es.onmessage = (e: MessageEvent<string>) => {
    try {
      const parsed = JSON.parse(e.data) as WorkflowSseEvent
      if (parsed && typeof parsed.type === 'string') {
        handlers.onEvent?.(parsed)
      }
    } catch {
      /* ignore non-JSON payloads */
    }
  }

  es.onerror = (ev) => handlers.onError?.(ev)

  return {
    close: () => {
      es.close()
    },
    eventSource: es,
  }
}

export interface CreateWorkflowPayload {
  document_id: string
  template_id: string
  start_immediately?: boolean
}

export async function createWorkflow(
  payload: CreateWorkflowPayload
): Promise<WorkflowCreateData> {
  const res = await client.post<WorkflowCreateData>('/workflow-runs', {
    document_id: payload.document_id,
    template_id: payload.template_id,
    start_immediately: payload.start_immediately ?? true,
  })
  return res.data as WorkflowCreateData
}

export async function getWorkflowStatus(workflowRunId: string): Promise<WorkflowStatusData> {
  const res = await client.get<WorkflowStatusData>(`/workflow-runs/${workflowRunId}/status`)
  return res.data as WorkflowStatusData
}

export async function getWorkflow(workflowRunId: string): Promise<WorkflowStatusData> {
  const res = await client.get<WorkflowStatusData>(`/workflow-runs/${workflowRunId}`)
  return res.data as WorkflowStatusData
}
