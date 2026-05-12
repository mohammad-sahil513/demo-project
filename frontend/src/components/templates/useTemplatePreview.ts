/**
 * Shared hook that loads a template's preview artifacts and renders the
 * DOCX preview into a caller-provided container.
 *
 * Behavior:
 *
 * - Fetches the full :{@link TemplateDto} metadata first.
 * - For DOCX templates, downloads the preview binary and renders it via
 *   `docx-preview`'s `renderAsync` into the supplied container element.
 *   The container reference is allowed to be `null` (e.g. before the
 *   modal mounts the slot); the hook waits until a real element is
 *   provided.
 * - For XLSX templates, fetches the HTML preview string from the
 *   backend and exposes it via `previewHtml` so the consumer can render
 *   it with `dangerouslySetInnerHTML`.
 *
 * The `reloadPreview` function is intentionally stable (memoized) so it
 * can be used as an effect dependency without causing infinite loops.
 */
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
        try {
          const binary = await templateApi.getTemplatePreviewBinary(templateId)
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
        } catch (err: unknown) {
          setError(getApiErrorMessage(err, 'Could not load generated DOCX preview.'))
          return
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
