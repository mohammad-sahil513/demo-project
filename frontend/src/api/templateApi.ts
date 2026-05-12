/**
 * Template API — list, upload, compile-status, schema, fidelity, downloads.
 *
 * The backend distinguishes inbuilt templates (PDD / SDD / UAT) from
 * custom uploads; both surface through `/api/templates/*`. The DTO
 * mapper (`dtoToTemplate`) collapses status + type into the `is_custom`
 * flag that the store consumes so views can decide between rendering
 * inbuilt-style cards and full custom template controls.
 */
import client from './client'
import type {
  TemplateDto,
  TemplateListData,
  TemplatePreviewHtmlData,
  TemplateSchemaData,
  TemplateValidationData,
} from './types'
import type { Template } from '../store/useJobStore'

function dtoToTemplate(d: TemplateDto): Template {
  const t = (d.template_type || '').toUpperCase()
  const isCustom =
    t === 'CUSTOM' ||
    d.status === 'UPLOADED' ||
    (d.template_type != null && !['PDD', 'SDD', 'UAT'].includes(t))
  return {
    id: d.template_id,
    template_id: d.template_id,
    filename: d.filename,
    type: d.template_type || d.template_id,
    template_type: d.template_type,
    status: d.status,
    description: d.filename,
    sections_preview: [],
    is_custom: isCustom,
    compile_error: d.compile_error ?? null,
    schema_version: d.schema_version ?? null,
    validation_status: d.validation_status ?? null,
    placeholder_schema: d.placeholder_schema ?? {},
    validation_errors: d.validation_errors ?? [],
    validation_warnings: d.validation_warnings ?? [],
    section_placeholder_bindings: d.section_placeholder_bindings ?? {},
    resolved_section_bindings: d.resolved_section_bindings ?? {},
  }
}

export interface TemplateUploadPayload {
  file: File
  template_type: string
  version?: string
}

export interface TemplatePreview {
  id: string
  type: string
  description: string
  sections_preview: string[]
  content?: string
  section_details?: Array<{ title: string; description: string }>
}

export const templateApi = {
  listTemplates: async (): Promise<Template[]> => {
    const res = await client.get<TemplateListData>('/templates')
    const data = res.data
    return (data.items ?? []).map(dtoToTemplate)
  },

  getTemplateRaw: async (templateId: string): Promise<TemplateDto> => {
    const res = await client.get<TemplateDto>(`/templates/${templateId}`)
    return res.data
  },

  getTemplateBinary: async (templateId: string): Promise<ArrayBuffer> => {
    const res = await client.get<ArrayBuffer>(`/templates/${templateId}/download`, {
      responseType: 'arraybuffer',
    })
    return res.data
  },

  getTemplatePreviewBinary: async (templateId: string): Promise<ArrayBuffer> => {
    const res = await client.get<ArrayBuffer>(`/templates/${templateId}/preview-binary`, {
      responseType: 'arraybuffer',
    })
    return res.data
  },

  getTemplatePreview: async (templateId: string): Promise<TemplatePreview> => {
    const raw = await templateApi.getTemplateRaw(templateId)
    return {
      id: raw.template_id,
      type: raw.template_type || raw.template_id,
      description: raw.filename,
      sections_preview: [],
    }
  },

  getTemplatePreviewHtml: async (templateId: string): Promise<TemplatePreviewHtmlData> => {
    const res = await client.get<TemplatePreviewHtmlData>(`/templates/${templateId}/preview-html`)
    return res.data
  },

  getTemplateSchema: async (templateId: string): Promise<TemplateSchemaData> => {
    const res = await client.get<TemplateSchemaData>(`/templates/${templateId}/schema`)
    return res.data
  },

  validateTemplate: async (templateId: string): Promise<TemplateValidationData> => {
    const res = await client.post<TemplateValidationData>(`/templates/${templateId}/validate`)
    return res.data
  },

  uploadTemplate: async (payload: TemplateUploadPayload) => {
    const form = new FormData()
    form.append('file', payload.file)
    form.append('template_type', payload.template_type)
    if (payload.version) form.append('version', payload.version)
    const res = await client.post('/templates/upload', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return res.data
  },

  deleteTemplate: async (templateId: string) => {
    const res = await client.delete(`/templates/${templateId}`)
    return res.data
  },

  /** Replace explicit section_id → placeholder_id map (JSON body). */
  updateSectionBindings: async (templateId: string, bindings: Record<string, string | string[]>) => {
    const res = await client.patch<TemplateDto>(`/templates/${templateId}/bindings`, bindings)
    return res.data
  },
}
