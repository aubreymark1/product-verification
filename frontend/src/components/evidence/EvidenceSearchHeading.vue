<script setup lang="ts">
import { Radar } from 'lucide-vue-next'
</script>

<template>
  <div class="evidence-search-heading">
    <div class="evidence-search-icon">
      <Radar :size="19" :stroke-width="1.8" />
    </div>

    <div class="evidence-search-copy">
      <h3>全网寻找证据</h3>
      <p>正在聚合测评、评论与商品评价</p>
    </div>
  </div>
</template>

<style scoped>
.evidence-search-heading {
  display: flex;
  align-items: center;
  gap: 9px;
  margin: 2px 0 0;
}

.evidence-search-icon {
  width: 30px;
  height: 30px;
  display: grid;
  place-items: center;
  flex: 0 0 30px;
  color: #69e7dc;
  background: rgba(35, 211, 196, 0.1);
  border: 1px solid rgba(78, 229, 216, 0.18);
  border-radius: 10px;
  animation: searchBreath 2.8s ease-in-out infinite;
}

.evidence-search-copy {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.evidence-search-copy h3 {
  margin: 0;
  color: rgba(255, 255, 255, 0.92);
  font-size: 14px;
  font-weight: 500;
  line-height: 1.4;
}

.evidence-search-copy p {
  margin: 0;
  color: rgba(255, 255, 255, 0.42);
  font-size: 11px;
  font-weight: 400;
  line-height: 1.4;
}

@keyframes searchBreath {
  0%,
  100% {
    opacity: 0.82;
  }

  50% {
    opacity: 1;
  }
}

@media (prefers-reduced-motion: reduce) {
  .evidence-search-icon {
    animation: none;
  }
}
</style>
