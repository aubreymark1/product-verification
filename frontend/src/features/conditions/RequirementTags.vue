<script setup lang="ts">
import { computed } from 'vue'

export interface RequirementItem {
  key: string
  label: string
  status: 'met' | 'unmet' | 'neutral'
}

const props = defineProps<{
  conditions?: Record<string, unknown>
  rawQuery?: string
}>()

const requirements = computed<RequirementItem[]>(() => {
  const result: RequirementItem[] = []
  const conds = props.conditions || {}

  for (const [k, v] of Object.entries(conds)) {
    if (v === undefined || v === null || v === '') continue

    let label = ''
    let status: 'met' | 'unmet' | 'neutral' = 'met'

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
      if (k.includes('budget') || k.includes('price') || k.includes('预算')) {
        label = `预算 ≤${v}元`
        status = 'unmet'
      }
    } else {
      label = String(v)
    }

    if (label) {
      result.push({ key: k, label, status })
    }
  }

  if (result.length === 0) {
    result.push(
      { key: 'game', label: 'FPS 游戏', status: 'met' },
      { key: 'wireless', label: '无线连接', status: 'met' },
      { key: 'weight', label: '轻量化', status: 'met' },
      { key: 'budget', label: '预算 ≤300元', status: 'unmet' }
    )
  }

  return result
})
</script>

<template>
  <div class="my-requirements-card">
    <div class="card-title">你的使用条件</div>
    <div class="chips-row">
      <span
        v-for="item in requirements"
        :key="item.key"
        class="compact-req-tag"
        :class="item.status"
      >
        <!-- Circle Checkmark Icon for Met -->
        <span v-if="item.status === 'met'" class="circle-icon met-icon">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="9" />
            <path d="M8.5 12.5l2.5 2.5 5-5" />
          </svg>
        </span>

        <!-- Circle Cross Icon for Unmet -->
        <span v-else-if="item.status === 'unmet'" class="circle-icon unmet-icon">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="9" />
            <line x1="15" y1="9" x2="9" y2="15" />
            <line x1="9" y1="9" x2="15" y2="15" />
          </svg>
        </span>

        <span class="tag-text">{{ item.label }}</span>
      </span>
    </div>
  </div>
</template>

<style scoped>
.my-requirements-card {
  background: #121824;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  padding: 12px 14px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.card-title {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
  font-weight: 500;
}

.chips-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.compact-req-tag {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 4px 10px;
  border-radius: 5px;
  font-size: 11px;
  font-weight: 400;
  background: rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.65);
  transition: all 0.15s ease;
}

/* 符合 (met) - 标签变绿 + 圆圈打勾 */
.compact-req-tag.met {
  background: rgba(16, 185, 129, 0.12);
  border: 1px solid rgba(16, 185, 129, 0.25);
  color: #10b981;
}

.met-icon {
  color: #10b981;
  display: flex;
  align-items: center;
}

/* 不符合 (unmet) - 标签变红 + 圆圈打叉 */
.compact-req-tag.unmet {
  background: rgba(239, 68, 68, 0.12);
  border: 1px solid rgba(239, 68, 68, 0.25);
  color: #f87171;
}

.unmet-icon {
  color: #f87171;
  display: flex;
  align-items: center;
}

/* 未提及 (neutral) - 保持不变 */
.compact-req-tag.neutral {
  background: rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.6);
}

.circle-icon {
  display: flex;
  align-items: center;
}

.tag-text {
  letter-spacing: 0.1px;
}
</style>
