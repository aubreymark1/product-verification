const leadingFillers = /^(?:我(?:平时)?(?:想|要|希望|需要)?|想要|希望|需要|主要(?:是)?|用来|用于|拿来|想买(?:个)?|买(?:个)?|最好|偏好)\s*/u
const trailingFillers = /(?:的|啊|呀|呢|吧)$/u

function normalizeSegment(segment: string): string {
  return segment
    .trim()
    .replace(leadingFillers, '')
    .replace(trailingFillers, '')
    .replace(/\s+/gu, ' ')
    .trim()
}

/**
 * Extracts the user's own requirement phrases without relying on a product
 * category or a fixed vocabulary. Punctuation and connective words separate
 * the phrases users commonly enter in a single natural-language sentence.
 */
export function extractRequirementKeywords(rawQuery: string, maxItems = 6): string[] {
  const normalizedQuery = rawQuery.trim()
  if (!normalizedQuery) return []

  const segments = normalizedQuery
    .split(/[，,、；;。！？!?\n]+|以及|或者|并且|同时|还有|跟|和/gu)
    .map(normalizeSegment)
    .filter((segment) => segment.length > 0)

  const uniqueSegments = new Set<string>()
  const keywords: string[] = []
  for (const segment of segments) {
    const dedupeKey = segment.toLocaleLowerCase()
    if (uniqueSegments.has(dedupeKey)) continue
    uniqueSegments.add(dedupeKey)
    keywords.push(segment)
    if (keywords.length === maxItems) break
  }

  return keywords.length > 0 ? keywords : [normalizedQuery]
}
