<script setup lang="ts">
import { computed } from 'vue'
import { CircleCheck, CircleX } from 'lucide-vue-next'

import { extractRequirementKeywords } from './requirementKeywords'
import type { RequirementAnalysisItem } from '../../types/api'

export interface RequirementItem {
  key: string
  label: string
  status: 'met' | 'unmet' | 'neutral'
}

const props = defineProps<{
  conditions?: Record<string, unknown>
  rawQuery?: string
  requirementAnalysis?: RequirementAnalysisItem[]
}>()

const requirements = computed<RequirementItem[]>(() => {
  const analysisItems = props.requirementAnalysis || []
  if (analysisItems.length > 0) {
    return analysisItems.map((item) => ({
      key: item.requirement_id,
      label: item.value || item.label,
      status: item.status === 'satisfied'
        ? 'met'
        : item.status === 'conflict'
          ? 'unmet'
          : 'neutral',
    }))
  }

  const keywords = extractRequirementKeywords(props.rawQuery || '')
  if (keywords.length > 0) {
    return keywords.map((label, index) => ({
      key: `query-${index}-${label}`,
      label,
      status: 'neutral',
    }))
  }

  const result: RequirementItem[] = []
  const conds = props.conditions || {}

  for (const [k, v] of Object.entries(conds)) {
    if (v === undefined || v === null || v === '') continue

    let label = ''
    const status: 'met' | 'unmet' | 'neutral' = 'neutral'

    if (Array.isArray(v)) {
      v.forEach((subItem) => {
        result.push({
          key: `${k}-${subItem}`,
          label: String(subItem),
          status: 'met',
        })
      })
      continue
    } else if (typeof v === 'boolean') {
      if (v) label = k
      else continue
    } else if (typeof v === 'number') {
      label = `${k} <= ${v}`
    } else {
      label = String(v)
    }

    if (label) {
      result.push({ key: k, label, status })
    }
  }

  return result
})
</script>

<template>
  <div class="my-requirements-card">
    <div class="card-title">我的需求</div>
    <div v-if="requirements.length" class="chips-row">
      <span
        v-for="item in requirements"
        :key="item.key"
        class="compact-req-tag"
        :class="item.status"
      >
        <span v-if="item.status === 'met'" class="circle-icon met-icon">
          <CircleCheck :size="11" :stroke-width="2.2" />
        </span>

        <span v-else-if="item.status === 'unmet'" class="circle-icon unmet-icon">
          <CircleX :size="11" :stroke-width="2.2" />
        </span>

        <span class="tag-text">{{ item.label }}</span>
      </span>
    </div>
    <p v-else class="empty-state">输入需求后将自动提取关键词</p>
  </div>
</template>

<style scoped>
.my-requirements-card {
  background:
    radial-gradient(circle at 0% 0%, rgba(255, 255, 255, 0.06), transparent 38%),
    rgba(13, 23, 35, 0.82);
  border: 1px solid rgba(255, 255, 255, 0.075);
  border-radius: 14px;
  padding: 10px 12px;
  display: flex;
  flex-direction: column;
  gap: 7px;
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.035),
    0 8px 18px rgba(0, 0, 0, 0.11);
}

.card-title {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.88);
  font-weight: 500;
  line-height: 1.45;
}

.chips-row {
  display: flex;
  gap: 3px;
  flex-wrap: wrap;
}

.empty-state {
  margin: 0;
  color: rgba(255, 255, 255, 0.55);
  font-size: 11px;
}

.compact-req-tag {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  height: 21px;
  min-width: 0;
  padding: 0 4px;
  border-radius: 7px;
  font-size: 9px;
  font-weight: 500;
  line-height: 1;
  background: rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.7);
  transition: all 0.15s ease;
}

.compact-req-tag.met {
  background: rgba(35, 211, 196, 0.1);
  border: 1px solid rgba(35, 211, 196, 0.18);
  color: rgba(105, 231, 220, 0.86);
}

.met-icon {
  color: rgba(105, 231, 220, 0.9);
  display: flex;
  align-items: center;
}

.compact-req-tag svg {
  width: 11px;
  height: 11px;
  flex: 0 0 auto;
}

.compact-req-tag.unmet {
  background: rgba(255, 72, 92, 0.095);
  border: 1px solid rgba(255, 72, 92, 0.16);
  color: rgba(255, 129, 142, 0.86);
}

.unmet-icon {
  color: rgba(255, 129, 142, 0.88);
  display: flex;
  align-items: center;
}

.compact-req-tag.neutral {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.06);
  color: rgba(255, 255, 255, 0.6);
}

.circle-icon {
  display: flex;
  align-items: center;
}

.tag-text {
  letter-spacing: 0;
  white-space: nowrap;
  line-height: 1;
}

@media (max-width: 390px) {
  .compact-req-tag {
    font-size: 9px;
    padding: 0 4px;
  }
}


/* Douyin theme: Douyin light requirement chips. */
.my-requirements-card {
  background: #ffffff;
  border-color: #ececee;
  box-shadow: 0 2px 10px rgba(22, 24, 35, 0.04);
}

.card-title { color: #24252b; }

.compact-req-tag {
  color: #707178;
  background: #f7f7f8;
  border: 1px solid #e7e7e9;
}

.compact-req-tag.met {
  color: #009f99;
  background: #edfffd;
  border-color: #8de5e1;
}

.met-icon { color: #00b5ad; }

.compact-req-tag.unmet {
  color: #ff3f65;
  background: #fff3f5;
  border-color: #ffb5c5;
}

.unmet-icon { color: #ff3f65; }

.compact-req-tag.neutral {
  color: #707178;
  background: #f5f5f6;
  border-color: #e8e8ea;
}

.empty-state { color: #8a8b91; }
</style>
