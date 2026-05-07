/** Backend success envelope (unwrapped by axios interceptor). */
export interface ApiEnvelope<T = unknown> {
  success: boolean
  message: string
  data: T
  errors: unknown[]
  meta: Record<string, unknown>
}

export interface DocumentUploadData {
  document_id: string
  filename: string
  content_type?: string
  size?: number
  status?: string
  created_at?: string
}

export interface WorkflowCreateData {
  workflow_run_id: string
  status: string
  current_phase: string
  overall_progress_percent: number
  document_id: string
  template_id: string | null
  output_id: string | null
  dispatch_mode?: string | null
  created_at?: string
  updated_at?: string
  [key: string]: unknown
}

export interface CitationDto {
  path: string
  page?: number | null
  content_type?: string
  chunk_id: string
}

export interface SectionEvidenceBundleDto {
  context_text?: string
  citations?: CitationDto[]
}

export interface AssembledSectionRow {
  section_id: string
  title: string
  execution_order?: number
  output_type?: string
  content?: string | null
  metadata?: Record<string, unknown>
}

export interface AssembledDocumentData {
  workflow_run_id: string
  template_id: string | null
  total_sections: number
  title: string
  sections: AssembledSectionRow[]
}

export interface WorkflowStatusData extends Record<string, unknown> {
  workflow_run_id: string
  status: string
  current_phase: string
  overall_progress_percent: number
  current_step_label?: string | null
  document_id: string
  template_id: string | null
  output_id: string | null
  assembled_document?: AssembledDocumentData | null
  section_retrieval_results?: Record<string, SectionEvidenceBundleDto>
}

export interface TemplateDto {
  template_id: string
  filename: string
  template_type: string | null
  version: string | null
  status: string
  created_at: string
  updated_at: string
  preview_path?: string | null
  preview_html?: string | null
  section_plan?: Array<Record<string, unknown>>
  style_map?: Record<string, unknown>
  sheet_map?: Record<string, unknown>
  compile_error?: string | null
  template_source?: string
  file_path?: string | null
  compiled_at?: string | null
  schema_version?: string | null
  placeholder_schema?: Record<string, unknown>
  validation_status?: string
  validation_errors?: Array<Record<string, unknown>>
  validation_warnings?: Array<Record<string, unknown>>
  /** User PATCH: section_id → placeholder_id(s) */
  section_placeholder_bindings?: Record<string, string | string[]>
  /** Compile output: section_id → bound placeholder ids */
  resolved_section_bindings?: Record<string, string[]>
  /** Server-inferred DOCX export branch for current flags + bindings */
  export_path_hint?: string
}

export interface TemplateListData {
  items: TemplateDto[]
  total: number
}

export interface TemplatePreviewHtmlData {
  html: string
  sheet_map?: Record<string, unknown>
}

export interface TemplateSchemaData {
  template_id: string
  schema_version?: string | null
  validation_status?: string
  placeholder_schema?: Record<string, unknown>
}

export interface TemplateValidationData {
  template_id: string
  validation_status?: string
  errors?: Array<Record<string, unknown>>
  warnings?: Array<Record<string, unknown>>
}
