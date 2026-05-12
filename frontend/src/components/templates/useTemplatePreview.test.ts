import { beforeEach, describe, expect, it, vi } from 'vitest'

const stateStore: unknown[] = []
let stateIndex = 0

const {
  renderAsyncMock,
  getTemplateRawMock,
  getTemplatePreviewBinaryMock,
  getTemplateBinaryMock,
  getTemplatePreviewHtmlMock,
} = vi.hoisted(() => ({
  renderAsyncMock: vi.fn(async () => undefined),
  getTemplateRawMock: vi.fn(),
  getTemplatePreviewBinaryMock: vi.fn(),
  getTemplateBinaryMock: vi.fn(),
  getTemplatePreviewHtmlMock: vi.fn(),
}))

vi.mock('react', () => ({
  useState: (initialValue: unknown) => {
    const idx = stateIndex++
    if (typeof stateStore[idx] === 'undefined') {
      stateStore[idx] = initialValue
    }
    const setState = (value: unknown) => {
      stateStore[idx] = typeof value === 'function' ? (value as (prev: unknown) => unknown)(stateStore[idx]) : value
    }
    return [stateStore[idx], setState]
  },
  useCallback: <T extends (...args: unknown[]) => unknown>(fn: T) => fn,
}))

vi.mock('docx-preview', () => ({
  renderAsync: renderAsyncMock,
}))

vi.mock('../../api/templateApi', () => ({
  templateApi: {
    getTemplateRaw: getTemplateRawMock,
    getTemplatePreviewBinary: getTemplatePreviewBinaryMock,
    getTemplateBinary: getTemplateBinaryMock,
    getTemplatePreviewHtml: getTemplatePreviewHtmlMock,
  },
}))

vi.mock('../../api/errors', () => ({
  getApiErrorMessage: (_err: unknown, fallback: string) => fallback,
}))

import { useTemplatePreview } from './useTemplatePreview'

describe('useTemplatePreview', () => {
  beforeEach(() => {
    stateStore.length = 0
    stateIndex = 0
    vi.clearAllMocks()
  })

  it('uses generated DOCX preview only (no download fallback)', async () => {
    getTemplateRawMock.mockResolvedValue({
      template_id: 'tpl-docx',
      template_type: 'PDD',
      filename: 'template.docx',
    })
    getTemplatePreviewBinaryMock.mockResolvedValue(new ArrayBuffer(8))

    const hook = useTemplatePreview({ templateId: 'tpl-docx' })
    const container = { innerHTML: '' } as HTMLDivElement

    await hook.reloadPreview(container)

    expect(getTemplatePreviewBinaryMock).toHaveBeenCalledWith('tpl-docx')
    expect(getTemplateBinaryMock).not.toHaveBeenCalled()
    expect(renderAsyncMock).toHaveBeenCalledTimes(1)
  })

  it('surfaces DOCX preview-binary failure and does not call download endpoint', async () => {
    getTemplateRawMock.mockResolvedValue({
      template_id: 'tpl-docx-fail',
      template_type: 'PDD',
      filename: 'template.docx',
    })
    getTemplatePreviewBinaryMock.mockRejectedValue(new Error('missing preview'))

    const hook = useTemplatePreview({ templateId: 'tpl-docx-fail' })
    await hook.reloadPreview({ innerHTML: '' } as HTMLDivElement)

    expect(getTemplatePreviewBinaryMock).toHaveBeenCalledWith('tpl-docx-fail')
    expect(getTemplateBinaryMock).not.toHaveBeenCalled()
    expect(stateStore[1]).toBe('Could not load generated DOCX preview.')
  })

  it('keeps XLSX preview path behavior', async () => {
    getTemplateRawMock.mockResolvedValue({
      template_id: 'tpl-xlsx',
      template_type: 'UAT',
      filename: 'template.xlsx',
    })
    getTemplatePreviewHtmlMock.mockResolvedValue({ html: '<div>Sheet preview</div>' })

    const hook = useTemplatePreview({ templateId: 'tpl-xlsx' })
    await hook.reloadPreview()

    expect(getTemplatePreviewHtmlMock).toHaveBeenCalledWith('tpl-xlsx')
    expect(getTemplatePreviewBinaryMock).not.toHaveBeenCalled()
    expect(getTemplateBinaryMock).not.toHaveBeenCalled()
    expect(stateStore[3]).toBe('<div>Sheet preview</div>')
  })
})
