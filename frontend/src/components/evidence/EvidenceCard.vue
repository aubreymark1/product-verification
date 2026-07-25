<script setup lang="ts">
import { ref } from 'vue'
import type { Conclusion } from '../../types/api'

const props = defineProps<{
  type: 'risk' | 'support' | 'uncertain'
  title: string
  items: Conclusion[]
}>()

const emit = defineEmits<{
  selectEvidence: [id: string]
}>()

const isExpanded = ref(true)

function toggleExpand() {
  isExpanded.value = !isExpanded.value
}
</script>

<template>
  <div class="evidence-accordion-card" :class="type">
    <div class="accordion-header" @click="toggleExpand">
      <div class="left-title-group">
        <span class="icon-circle">
          {{ type === 'risk' ? '!' : type === 'support' ? '✓' : '?' }}
        </span>
        <span class="title-text">{{ title }}</span>
      </div>

      <div class="right-meta">
        <span class="count-text">{{ items.length }}条</span>
        <span class="chevron" :class="{ open: isExpanded }">&gt;</span>
      </div>
    </div>

    <div v-if="isExpanded && items.length > 0" class="accordion-body">
      <div
        v-for="item in items"
        :key="item.id"
        class="evidence-item-row"
        @click="emit('selectEvidence', item.source_ids[0] || item.id)"
      >
        <span class="claim-text">{{ item.claim }}</span>
        <span class="row-arrow">&gt;</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.evidence-accordion-card {
  background: #121824;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  overflow: hidden;
}

.evidence-accordion-card.risk {
  border-color: rgba(239, 68, 68, 0.25);
}

.evidence-accordion-card.support {
  border-color: rgba(16, 185, 129, 0.25);
}

.evidence-accordion-card.uncertain {
  border-color: rgba(245, 158, 11, 0.25);
}

.accordion-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 14px;
  cursor: pointer;
  user-select: none;
}

.left-title-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.icon-circle {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 800;
}

.risk .icon-circle {
  background: #ef4444;
  color: #ffffff;
}

.support .icon-circle {
  background: #10b981;
  color: #ffffff;
}

.uncertain .icon-circle {
  background: #f59e0b;
  color: #ffffff;
}

.title-text {
  font-size: 14px;
  font-weight: 600;
  color: #ffffff;
}

.right-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

.chevron {
  font-size: 11px;
  transition: transform 0.2s ease;
}

.chevron.open {
  transform: rotate(90deg);
}

.accordion-body {
  display: flex;
  flex-direction: column;
  padding: 0 10px 10px;
  gap: 6px;
}

.evidence-item-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(255, 255, 255, 0.04);
  border-radius: 5px;
  padding: 10px 12px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.75);
  cursor: pointer;
  transition: background 0.15s ease;
}

.evidence-item-row:hover {
  background: rgba(255, 255, 255, 0.08);
  color: #ffffff;
}

.claim-text {
  line-height: 1.4;
}

.row-arrow {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.4);
}
</style>
