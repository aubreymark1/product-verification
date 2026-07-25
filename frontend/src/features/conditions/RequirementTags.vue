<script setup lang="ts">
import { computed } from 'vue'
import { CircleCheck, CircleX } from 'lucide-vue-next'

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
        label = `预算 ≤ ${v}元`
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

  const order = ['FPS 游戏', '无线连接', '轻量化', '预算 ≤ 300元']
  return result.sort((a, b) => {
    const aIndex = order.indexOf(a.label)
    const bIndex = order.indexOf(b.label)
    return (aIndex === -1 ? order.length : aIndex) - (bIndex === -1 ? order.length : bIndex)
  })
})
</script>

<template>
  <div class="my-requirements-card">
    <div class="card-title">我的需求</div>
    <div class="chips-row">
      <span
        v-for="item in requirements"
        :key="item.key"
        class="compact-req-tag"
        :class="item.status"
      >
        <span v-if="item.status === 'met'" class="circle-icon met-icon">
          <CircleCheck :size="15" :stroke-width="1.8" />
        </span>

        <span v-else-if="item.status === 'unmet'" class="circle-icon unmet-icon">
          <CircleX :size="15" :stroke-width="1.8" />
        </span>

        <span class="tag-text">{{ item.label }}</span>
      </span>
    </div>
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
  gap: 4px;
  flex-wrap: nowrap;
  overflow: hidden;
}

.compact-req-tag {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  height: 25px;
  min-width: 0;
  padding: 0 5px;
  border-radius: 8px;
  font-size: 10px;
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
  width: 13px;
  height: 13px;
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
    font-size: 10px;
    padding: 0 5px;
  }
}
</style>
