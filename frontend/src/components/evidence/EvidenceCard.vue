<script setup lang="ts">
import { computed } from 'vue'

import EvidenceSection from './EvidenceSection.vue'
import type { Conclusion, DemoInsightItem, DemoReview } from '../../types/api'

const props = defineProps<{
  type: 'risk' | 'support' | 'uncertain'
  title: string
  items: Conclusion[]
  demoReviews?: DemoReview[]
  demoItems?: DemoInsightItem[]
  expanded?: boolean
}>()

const emit = defineEmits<{
  selectEvidence: [id: string]
}>()

const evidenceType = computed(() => (props.type === 'uncertain' ? 'pending' : props.type))
</script>

<template>
  <EvidenceSection
    :type="evidenceType"
    :title="title"
    :items="items"
    :demo-reviews="demoReviews"
    :demo-items="demoItems"
    :expanded="expanded"
    @select-evidence="emit('selectEvidence', $event)"
  />
</template>
