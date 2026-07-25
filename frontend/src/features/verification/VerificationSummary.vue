<script setup lang="ts">
import { SearchCheck } from 'lucide-vue-next'

defineProps<{
  productName: string
}>()
</script>

<template>
  <div class="verification-summary">
    <div class="verification-summary__icon">
      <SearchCheck :size="19" :stroke-width="1.8" />
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
  background:
    radial-gradient(
      ellipse at 0% 50%,
      rgba(26, 222, 207, 0.17),
      transparent 44%
    ),
    radial-gradient(
      ellipse at 100% 50%,
      rgba(39, 105, 255, 0.11),
      transparent 48%
    ),
    linear-gradient(
      105deg,
      rgba(7, 41, 47, 0.94),
      rgba(5, 17, 29, 0.98) 52%,
      rgba(8, 21, 41, 0.97)
    );
  border: 1px solid rgba(76, 219, 227, 0.26);
  border-radius: 14px;
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.05),
    0 8px 24px rgba(0, 0, 0, 0.18);
}

.verification-summary::after {
  content: '';
  position: absolute;
  inset: 0;
  pointer-events: none;
  background: linear-gradient(
    110deg,
    transparent 20%,
    rgba(255, 255, 255, 0.035) 45%,
    transparent 68%
  );
}

.verification-summary__icon {
  position: relative;
  z-index: 1;
  width: 36px;
  height: 36px;
  display: grid;
  place-items: center;
  color: #69e7dc;
  background: rgba(35, 211, 196, 0.11);
  border: 1px solid rgba(78, 229, 216, 0.2);
  border-radius: 12px;
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
  font-weight: 600;
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
