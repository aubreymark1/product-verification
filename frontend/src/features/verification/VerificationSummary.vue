<script setup lang="ts">
import { Check } from 'lucide-vue-next'

defineProps<{
  productName: string
}>()
</script>

<template>
  <div class="verification-summary">
    <div class="verification-summary__icon">
      <Check :size="20" :stroke-width="2.4" />
    </div>
    <div class="verification-summary__text">
      当前证据支持<strong class="verification-summary__highlight">{{ productName }}</strong>较好满足你的需求，整体推荐购买。
    </div>
  </div>
</template>

<style scoped>
.verification-summary {
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  min-height: 76px;
  display: grid;
  grid-template-columns: 36px minmax(0, 1fr);
  column-gap: 12px;
  padding: 14px 16px;
  background: #07111d;
  border: 1px solid rgba(95, 205, 255, 0.58);
  border-radius: 14px;
  box-shadow:
    inset 0 0 18px rgba(105, 231, 220, 0.08),
    inset 0 1px 0 rgba(255, 255, 255, 0.06),
    0 0 0 1px rgba(105, 231, 220, 0.08),
    0 0 20px rgba(105, 231, 220, 0.22),
    0 0 28px rgba(59, 130, 246, 0.16),
    0 10px 24px rgba(0, 0, 0, 0.22);
}

.verification-summary::after {
  position: absolute;
  inset: 1px;
  pointer-events: none;
  border: 1px solid rgba(105, 231, 220, 0.14);
  border-radius: 13px;
  box-shadow:
    inset 0 0 18px rgba(105, 231, 220, 0.06),
    inset 0 0 28px rgba(59, 130, 246, 0.04);
  content: "";
}

.verification-summary__icon {
  position: relative;
  z-index: 1;
  width: 36px;
  height: 36px;
  display: grid;
  place-items: center;
  color: #69e7dc;
}

.verification-summary__text {
  position: relative;
  z-index: 1;
  min-width: 0;
  color: rgba(226, 232, 240, 0.94);
  font-size: 13px;
  font-weight: 400;
  line-height: 1.5;
}

.verification-summary__highlight {
  color: #69e7dc;
  font-weight: 700;
  text-shadow: 0 0 14px rgba(105, 231, 220, 0.28);
}

@media (max-width: 390px) {
  .verification-summary {
    padding: 14px 16px;
    border-radius: 14px;
  }

  .verification-summary__icon {
    width: 36px;
    height: 36px;
  }

  .verification-summary__text {
  font-size: 13px;
  }
}
</style>
