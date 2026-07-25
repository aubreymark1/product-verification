<script setup lang="ts">
import { computed, ref } from 'vue'
import {
  CircleAlert,
  CircleCheck,
  CircleHelp,
  ChevronDown,
  ChevronRight,
} from 'lucide-vue-next'

import type {
  EvidenceGroup,
  EvidenceItem,
} from './evidenceData'

const props = defineProps<{
  group: EvidenceGroup
  defaultExpanded?: boolean
}>()

const emit = defineEmits<{
  select: [item: EvidenceItem]
}>()

const expanded = ref(props.defaultExpanded ?? true)

const iconComponent = computed(() => {
  const iconMap = {
    risk: CircleAlert,
    support: CircleCheck,
    pending: CircleHelp,
  }

  return iconMap[props.group.type]
})

function selectEvidence(item: EvidenceItem) {
  emit('select', item)
}
</script>

<template>
  <section
    class="evidence-section"
    :class="`evidence-section--${group.type}`"
  >
    <button
      type="button"
      class="evidence-section__header"
      :aria-expanded="expanded"
      @click="expanded = !expanded"
    >
      <span class="evidence-section__icon">
        <component
          :is="iconComponent"
          :size="17"
          :stroke-width="1.9"
        />
      </span>

      <span class="evidence-section__title">
        {{ group.title }}
      </span>

      <span class="evidence-section__count">
        {{ group.items.length }} 条
      </span>

      <ChevronDown
        :size="16"
        class="evidence-section__expand"
        :class="{ 'is-expanded': expanded }"
      />
    </button>

    <div
      v-show="expanded"
      class="evidence-section__body"
    >
      <button
        v-for="item in group.items"
        :key="item.id"
        type="button"
        class="evidence-row"
        @click="selectEvidence(item)"
      >
        <span class="evidence-row__text">
          {{ item.title }}
        </span>

        <ChevronRight
          :size="15"
          :stroke-width="1.8"
          class="evidence-row__arrow"
        />
      </button>
    </div>
  </section>
</template>

<style scoped>
.evidence-section {
  --evidence-rgb: 35, 211, 196;
  --evidence-dark-rgb: 8, 44, 43;

  overflow: hidden;
  border: 1px solid rgba(var(--evidence-rgb), 0.14);
  border-radius: 12px;

  background:
    radial-gradient(
      circle at 0% 0%,
      rgba(var(--evidence-rgb), 0.1),
      transparent 46%
    ),
    linear-gradient(
      135deg,
      rgba(var(--evidence-dark-rgb), 0.74),
      rgba(6, 16, 25, 0.98) 58%
    );
}

.evidence-section--risk {
  --evidence-rgb: 255, 78, 98;
  --evidence-dark-rgb: 53, 18, 27;
}

.evidence-section--support {
  --evidence-rgb: 34, 210, 187;
  --evidence-dark-rgb: 8, 48, 45;
}

.evidence-section--pending {
  --evidence-rgb: 255, 163, 52;
  --evidence-dark-rgb: 54, 36, 13;
}

.evidence-section__header {
  display: grid;
  grid-template-columns: 24px minmax(0, 1fr) auto 16px;
  gap: 8px;
  align-items: center;

  width: 100%;
  min-height: 42px;
  padding: 7px 10px;

  color: white;
  text-align: left;
  background: transparent;
  border: 0;
  cursor: pointer;
}

.evidence-section__icon {
  display: grid;
  width: 22px;
  height: 22px;
  place-items: center;

  color: rgb(var(--evidence-rgb));
  background: rgba(var(--evidence-rgb), 0.13);
  border-radius: 50%;
}

.evidence-section__title {
  font-size: 14px;
  font-weight: 600;
}

.evidence-section__count {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.48);
}

.evidence-section__expand {
  color: rgba(255, 255, 255, 0.48);
  transition: transform 180ms ease;
}

.evidence-section__expand.is-expanded {
  transform: rotate(180deg);
}

.evidence-section__body {
  display: grid;
  gap: 5px;
  padding: 0 9px 9px;
}

.evidence-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 15px;
  gap: 8px;
  align-items: center;

  width: 100%;
  min-height: 32px;
  padding: 6px 9px;

  color: rgba(255, 255, 255, 0.74);
  text-align: left;

  background: rgba(255, 255, 255, 0.035);
  border: 1px solid rgba(255, 255, 255, 0.04);
  border-radius: 7px;
}

.evidence-row:active {
  background: rgba(255, 255, 255, 0.065);
}

.evidence-row__text {
  overflow: hidden;
  font-size: 11px;
  line-height: 1.4;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.evidence-row__arrow {
  color: rgba(255, 255, 255, 0.34);
}
</style>
