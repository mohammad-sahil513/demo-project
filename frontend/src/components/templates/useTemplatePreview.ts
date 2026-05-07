import { useCallback, useState } from 'react'
import { renderAsync } from 'docx-preview'
import { templateApi } from '../../api/templateApi'
import type { TemplateDto } from '../../api/types'
import { getApiErrorMessage } from '../../api/errors'

interface UseTemplatePreviewArgs {
  templateId: string
  fallbackTemplateType?: string
}

interface UseTemplatePreviewResult {
  loading: boolean
  error: string | null
  dto: TemplateDto | null
  previewHtml: string | null
  isXlsxPreview: boolean
  reloadPreview: (container?: HTMLDivElement | null) => Promise<void>
}

export function useTemplatePreview({
  templateId,
  fallbackTemplateType,
}: UseTemplatePreviewArgs): UseTemplatePreviewResult {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [dto, setDto] = useState<TemplateDto | null>(null)
  const [previewHtml, setPreviewHtml] = useState<string | null>(null)
  const [isXlsxPreview, setIsXlsxPreview] = useState(false)

  const reloadPreview = useCallback(async (container?: HTMLDivElement | null) => {
    if (!templateId) {
      setError('Template ID is missing.')
      setLoading(false)
      return
    }

    setLoading(true)
    setError(null)
    setPreviewHtml(null)

    try {
      const data = await templateApi.getTemplateRaw(templateId)
      setDto(data)

      const normalizedType = (data.template_type || fallbackTemplateType || '').toUpperCase()
      const lowerFilename = (data.filename || '').toLowerCase()
      const xlsxPreview = normalizedType === 'UAT' || lowerFilename.endsWith('.xlsx')
      setIsXlsxPreview(xlsxPreview)

      if (xlsxPreview) {
        try {
          const htmlData = await templateApi.getTemplatePreviewHtml(templateId)
          const html = (htmlData.html || '').trim()
          setPreviewHtml(html || '<div>No sheet preview available.</div>')
        } catch {
          setPreviewHtml('<div>No sheet preview available yet. Showing schema details below.</div>')
        }
      } else {
        let binary: ArrayBuffer
        try {
          binary = await templateApi.getTemplatePreviewBinary(templateId)
        } catch {
          binary = await templateApi.getTemplateBinary(templateId)
        }
        if (container) {
          container.innerHTML = ''
          await renderAsync(binary, container, undefined, {
            className: 'docx-preview-content',
            inWrapper: true,
            ignoreWidth: false,
            ignoreHeight: false,
            useBase64URL: true,
            renderHeaders: true,
            renderFooters: true,
            renderFootnotes: true,
            renderEndnotes: true,
          } as Parameters<typeof renderAsync>[3])
        }
      }
    } catch (err: unknown) {
      setError(getApiErrorMessage(err, 'Could not load template preview.'))
      setDto(null)
      setPreviewHtml(null)
    } finally {
      setLoading(false)
    }
  }, [templateId, fallbackTemplateType])

  return {
    loading,
    error,
    dto,
    previewHtml,
    isXlsxPreview,
    reloadPreview,
  }
}
