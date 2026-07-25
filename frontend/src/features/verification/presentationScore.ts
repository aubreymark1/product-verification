import type { VerificationResult } from '../../types/api'

/**
 * Returns a presentation-only score for the Mock demo UI.
 * The trusted recommendation_score remains untouched and is still governed by
 * the evidence chain. This fallback keeps older backend responses from making
 * every product appear as the same 35% result.
 */
export function presentationScore(result: VerificationResult | null | undefined): number {
  if (!result) return 0
  if (typeof result.demo_insights?.presentation_score === 'number') {
    return result.demo_insights.presentation_score
  }

  const fingerprint = [
    result.product.product_id,
    result.raw_query,
    ...Object.entries(result.conditions)
      .sort(([left], [right]) => left.localeCompare(right))
      .map(([key, value]) => `${key}:${String(value)}`),
  ].join('|')
  let hash = 0
  for (const char of fingerprint) {
    hash = (hash * 31 + char.charCodeAt(0)) >>> 0
  }
  const mixedHash = Math.imul(hash ^ (hash >>> 16), 0x45d9f3b) >>> 0
  return Number((0.52 + (mixedHash % 37) / 100).toFixed(2))
}
