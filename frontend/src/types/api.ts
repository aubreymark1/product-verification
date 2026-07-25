export interface ApiError {
  code: string
  message: string
}

export interface ApiResponse<T> {
  success: boolean
  data: T | null
  error: ApiError | null
}

export interface BBox {
  x: number
  y: number
  width: number
  height: number
}

export interface VideoObject {
  object_id: string
  category_id: string
  label: string
  bbox: BBox
}

export interface Video {
  video_id: string
  title: string
  video_url: string | null
  duration: number
  objects: VideoObject[]
}

export interface CandidateProduct {
  product_id: string
  product_name: string
  confidence: number
  image_url: string | null
}

export interface IdentifyResult {
  category_id: string
  category_name: string
  visual_attributes: Record<string, string>
  candidates: CandidateProduct[]
}

export type ConditionFieldType = 'single_select' | 'multi_select' | 'number' | 'text' | 'boolean'

export interface ConditionField {
  key: string
  label: string
  type: ConditionFieldType
  required: boolean
  options: string[]
  min?: number | null
  max?: number | null
}

export interface CategoryProfile {
  category_id: string
  category_name: string
  condition_fields: ConditionField[]
  verification_dimensions: { key: string; label: string }[]
}

export interface Conclusion {
  id: string
  claim: string
  source_ids: string[]
  confidence: number
}

export interface VerificationResult {
  result_id: string
  product: CandidateProduct
  conditions: Record<string, unknown>
  summary: string
  support: Conclusion[]
  risks: Conclusion[]
  uncertain: Conclusion[]
  confidence: number
}

export interface Evidence {
  evidence_id: string
  product_id: string
  category_id: string
  dimension: string
  source_type: 'official' | 'professional_test' | 'user_feedback' | 'demo_mock'
  relation_level: 'exact_product' | 'likely_same_product' | 'similar_product'
  summary: string
  content: string
  source_title: string
  source_platform: string
  source_url: string | null
  published_at: string | null
  confidence: number
}
