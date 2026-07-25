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

export type RequirementPriority = 'must' | 'important' | 'preference'
export type MatchStatus = 'satisfied' | 'conflict' | 'unknown'
export type AnalysisMode = 'ai' | 'rule' | 'degraded'

export interface ProductFact {
  fact_id: string
  key: string
  label: string
  value: string
  source_ids: string[]
  confidence: number
}

export interface RequirementAnalysisItem {
  requirement_id: string
  key: string
  label: string
  value: string
  priority: RequirementPriority
  weight: number
  status: MatchStatus
  rationale: string
  product_facts: ProductFact[]
  source_ids: string[]
}

export interface DecisionTrace {
  requirement_id: string
  requirement: string
  fact_ids: string[]
  source_ids: string[]
  status: MatchStatus
  conclusion: string
}

export interface UnknownItem {
  requirement_id: string
  label: string
  reason: string
  needed_evidence: string
}

export interface VerificationResult {
  result_id: string
  product: CandidateProduct
  conditions: Record<string, unknown>
  raw_query: string
  round: number
  is_follow_up: boolean
  needs_inherited: boolean
  recommendation_score: number
  recommendation_basis: RecommendationDimension[]
  requirement_analysis: RequirementAnalysisItem[]
  product_facts: ProductFact[]
  decision_chain: DecisionTrace[]
  unknown_items: UnknownItem[]
  analysis_mode: AnalysisMode
  change_summary: string
  summary: string
  support: Conclusion[]
  risks: Conclusion[]
  uncertain: Conclusion[]
  dissatisfaction_reasons: string[]
  purchase_channels: PurchaseChannel[]
  demo_insights?: DemoInsights | null
}

export interface RecommendationDimension {
  key: string
  label: string
  score: number
  rationale: string
  source_ids: string[]
}

export type PurchaseChannelType = 'official' | 'marketplace' | 'retail' | 'other'

export interface PurchaseChannel {
  channel_id: string
  product_id: string
  channel_name: string
  channel_type: PurchaseChannelType
  url: string | null
  availability: 'available' | 'pending' | 'placeholder'
  note: string
}

export interface DemoReview {
  review_id: string
  focus: string
  sentiment: 'positive' | 'mixed' | 'negative'
  rating: number
  content: string
  source_type: 'demo_mock'
}

export interface DemoPriceOffer {
  offer_id: string
  channel_name: string
  price: number
  original_price: number
  offer: string
  note: string
  source_type: 'demo_mock'
}

export interface DemoInsightItem {
  insight_id: string
  label: string
  content: string
  source_type: 'demo_mock'
}

export interface DemoInsights {
  is_mock: true
  scenario_id: string
  generated_by: 'demo_scenario_provider'
  generated_at: string
  personalization_note: string
  presentation_score: number
  reviews: DemoReview[]
  support_items: DemoInsightItem[]
  risk_items: DemoInsightItem[]
  pending_items: DemoInsightItem[]
  price_offers: DemoPriceOffer[]
}

export interface VerificationRequest {
  video_id: string
  product_id: string
  category_id: string
  conditions: Record<string, unknown>
  raw_query: string
  input_mode?: 'text' | 'voice' | 'mixed'
}

export interface RerunRecommendationRequest {
  video_id: string
  product_id: string
  category_id: string
  previous_result_id: string
  dissatisfaction_reasons: string[]
  dissatisfaction_note: string
  inherit_previous_needs: boolean
  conditions_patch: Record<string, unknown>
  raw_query: string
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
