<script setup lang="ts">
import { computed, ref } from 'vue'
import {
  ChevronDown,
  ChevronRight,
  ChevronUp,
  CircleAlert,
  CircleCheck,
  CircleHelp,
} from 'lucide-vue-next'

import type { Conclusion, DemoInsightItem, DemoReview } from '../../types/api'

type EvidenceType = 'support' | 'risk' | 'pending'

const props = withDefaults(defineProps<{
  type: EvidenceType
  title: string
  items: Conclusion[]
  expanded?: boolean
  demoReviews?: DemoReview[]
  demoItems?: DemoInsightItem[]
}>(), {
  expanded: false,
  demoReviews: () => [],
  demoItems: () => [],
})

const emit = defineEmits<{
  selectEvidence: [id: string]
}>()

const isExpanded = ref(props.expanded)

const typeIconMap = {
  support: CircleCheck,
  risk: CircleAlert,
  pending: CircleHelp,
}

const sectionIcon = computed(() => typeIconMap[props.type])
const sectionClass = computed(() => `evidence-card--${props.type}`)

function toggleExpand() {
  isExpanded.value = !isExpanded.value
}
</script>

<template>
    <section class="evidence-card" :class="[sectionClass, { 'is-empty': items.length === 0 && demoItems.length === 0, 'has-demo-reviews': demoReviews.length > 0 }]">
    <button
      class="evidence-card__header"
      type="button"
      :aria-expanded="isExpanded"
      @click="toggleExpand"
    >
      <span class="evidence-card__title-group">
        <span class="evidence-card__icon">
          <component :is="sectionIcon" :size="18" :stroke-width="1.8" />
        </span>
        <span class="evidence-card__title">{{ title }}</span>
      </span>

      <span class="evidence-card__meta">
        <span>{{ items.length + demoItems.length }} 条<span v-if="demoItems.length" class="demo-count">（含 {{ demoItems.length }} 条演示）</span></span>
        <ChevronUp v-if="isExpanded" :size="17" :stroke-width="1.8" />
        <ChevronDown v-else :size="17" :stroke-width="1.8" />
      </span>
    </button>

    <div class="evidence-card__body-shell" :class="{ open: isExpanded }">
      <div class="evidence-card__body">
        <button
          v-for="item in items"
          :key="item.id"
          class="evidence-item"
          type="button"
          @click="emit('selectEvidence', item.source_ids[0] || item.id)"
        >
          <span class="evidence-item__text">{{ item.claim }}</span>
          <ChevronRight class="evidence-item__icon" :size="15" :stroke-width="1.8" />
          </button>
          <div v-if="demoItems.length" class="demo-insight-evidence">
            <div class="demo-review-evidence__heading">
              <span>平台信息参考</span>
              <span>演示数据</span>
            </div>
            <article v-for="item in demoItems" :key="item.insight_id" class="demo-insight-evidence__item">
              <strong>{{ item.label }}</strong>
              <p>{{ item.content }}</p>
            </article>
          </div>
          <div v-if="demoReviews.length" class="demo-review-evidence">
            <div class="demo-review-evidence__heading">
              <span>平台口碑摘要</span>
              <span>演示数据</span>
            </div>
            <article v-for="review in demoReviews" :key="review.review_id" class="demo-review-evidence__item">
              <div class="demo-review-evidence__meta">
                <span>{{ review.focus }}</span>
                <strong>★ {{ review.rating.toFixed(1) }}</strong>
              </div>
              <p>{{ review.content }}</p>
            </article>
          </div>
        </div>
    </div>
  </section>
</template>

<style scoped>
.evidence-card {
  position: relative;
  overflow: hidden;
  border: 1px solid rgba(var(--evidence-rgb), 0.15);
  border-radius: 14px;
  background:
    radial-gradient(circle at 0% 0%, rgba(var(--evidence-rgb), 0.08), transparent 38%),
    linear-gradient(
      135deg,
      rgba(var(--evidence-dark-rgb), 0.6) 0%,
      rgba(7, 17, 27, 0.98) 58%,
      rgba(6, 14, 22, 0.99) 100%
    );
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.025),
    0 6px 16px rgba(0, 0, 0, 0.1);
}

.evidence-card--support {
  --evidence-rgb: 35, 211, 196;
  --evidence-dark-rgb: 9, 49, 46;
}

.evidence-card--risk {
  --evidence-rgb: 255, 72, 92;
  --evidence-dark-rgb: 55, 20, 28;
}

.evidence-card--pending {
  --evidence-rgb: 255, 164, 48;
  --evidence-dark-rgb: 55, 37, 15;
}

.evidence-card__header {
  height: 56px;
  width: 100%;
  display: grid;
  grid-template-columns: 28px minmax(0, 1fr) auto auto;
  align-items: center;
  column-gap: 8px;
  padding: 0 8px;
  color: inherit;
  background: transparent;
  border: 0;
  cursor: pointer;
  text-align: left;
}

.evidence-card__header:focus-visible,
.evidence-item:focus-visible {
  outline: 2px solid rgba(var(--evidence-rgb), 0.42);
  outline-offset: -2px;
}

.evidence-card__title-group {
  min-width: 0;
  display: contents;
}

.evidence-card__icon {
  width: 28px;
  height: 28px;
  display: grid;
  place-items: center;
  border-radius: 50%;
}

.evidence-card.is-empty .evidence-card__header {
  height: 40px;
}

.evidence-card--support .evidence-card__icon {
  color: #48dfc8;
  background: rgba(35, 211, 196, 0.12);
  border: 1px solid rgba(35, 211, 196, 0.18);
}

.evidence-card--risk .evidence-card__icon {
  color: #ff6275;
  background: rgba(255, 72, 92, 0.11);
  border: 1px solid rgba(255, 72, 92, 0.17);
}

.evidence-card--pending .evidence-card__icon {
  color: #ffb554;
  background: rgba(255, 164, 48, 0.11);
  border: 1px solid rgba(255, 164, 48, 0.17);
}

.evidence-card__title {
  min-width: 0;
  color: rgba(255, 255, 255, 0.92);
  font-size: 14px;
  font-weight: 500;
  line-height: 1.45;
  letter-spacing: 0;
}

.evidence-card__meta {
  display: contents;
}

.evidence-card__meta span {
  display: inline-flex;
  align-items: center;
  color: rgba(255, 255, 255, 0.36);
  font-size: 11px;
  font-weight: 400;
  line-height: 1;
}

.evidence-card__meta svg {
  color: rgba(255, 255, 255, 0.42);
}

.evidence-card__body-shell {
  display: grid;
  grid-template-rows: 0fr;
  overflow: hidden;
  opacity: 0;
  transition:
    grid-template-rows 180ms ease,
    opacity 180ms ease;
}

.evidence-card__body-shell.open {
  grid-template-rows: 1fr;
  opacity: 1;
}

.evidence-card__body {
  min-height: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 0 8px 8px;
}

.evidence-item {
  min-height: 34px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 7px 9px;
  color: rgba(255, 255, 255, 0.72);
  background: rgba(255, 255, 255, 0.035);
  border: 1px solid rgba(255, 255, 255, 0.045);
  border-radius: 8px;
  cursor: pointer;
  text-align: left;
  transition:
    background 150ms ease,
    color 150ms ease,
    border-color 150ms ease;
}

.evidence-item:hover {
  color: rgba(255, 255, 255, 0.9);
  background: rgba(255, 255, 255, 0.055);
  border-color: rgba(255, 255, 255, 0.07);
}

.evidence-item__text {
  min-width: 0;
  font-size: 12px;
  font-weight: 400;
  line-height: 1.6;
}

.evidence-item__icon {
  flex: 0 0 auto;
  color: rgba(255, 255, 255, 0.38);
}

.evidence-card__meta .demo-count {
  margin-left: 3px;
  color: #ffc66d;
  font-size: 10px;
}

.demo-review-evidence {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-top: 3px;
  padding-top: 9px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.demo-insight-evidence {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.demo-insight-evidence__item {
  padding: 8px 9px;
  background: rgba(255, 255, 255, 0.035);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
}

.demo-insight-evidence__item strong {
  color: rgba(255, 255, 255, 0.82);
  font-size: 11px;
  font-weight: 500;
}

.demo-insight-evidence__item p {
  margin: 5px 0 0;
  color: rgba(255, 255, 255, 0.68);
  font-size: 11px;
  line-height: 1.55;
}

.demo-review-evidence__heading,
.demo-review-evidence__meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.demo-review-evidence__heading {
  color: rgba(255, 255, 255, 0.48);
  font-size: 10px;
}

.demo-review-evidence__heading span:last-child {
  color: #ffc66d;
}

.demo-review-evidence__item {
  padding: 8px 9px;
  background: rgba(35, 211, 196, 0.045);
  border: 1px solid rgba(35, 211, 196, 0.1);
  border-radius: 8px;
}

.demo-review-evidence__meta {
  color: #9eece5;
  font-size: 10px;
}

.demo-review-evidence__meta strong {
  color: #ffd37a;
  font-weight: 500;
}

.demo-review-evidence__item p {
  margin: 5px 0 0;
  color: rgba(255, 255, 255, 0.68);
  font-size: 11px;
  line-height: 1.55;
}

@media (prefers-reduced-motion: reduce) {
  .evidence-card__body-shell,
  .evidence-item {
    transition: none;
  }
}
</style>
