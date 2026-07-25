<script setup lang="ts">
const props = withDefaults(
  defineProps<{
    score?: number
  }>(),
  {
    score: 0.82,
  }
)

const percent = Math.round(props.score * 100)
</script>

<template>
  <div class="gauge-ring-only">
    <div class="ring-wrapper">
      <svg class="ring-svg" viewBox="0 0 100 100">
        <defs>
          <linearGradient id="recommendation-gauge-gradient" x1="0%" y1="100%" x2="100%" y2="0%">
            <stop offset="0%" stop-color="#27c7d9" />
            <stop offset="100%" stop-color="#62a8ff" />
          </linearGradient>
        </defs>
        <!-- Background Track -->
        <circle cx="50" cy="50" r="40" class="ring-bg" />
        <!-- Progress Arc -->
        <circle
          cx="50"
          cy="50"
          r="40"
          class="ring-progress"
          stroke="url(#recommendation-gauge-gradient)"
          :stroke-dasharray="251.2"
          :style="{ '--ring-offset': `${251.2 * (1 - percent / 100)}` }"
        />
      </svg>

      <div class="ring-content">
        <span class="ring-label">推荐度</span>
        <div class="ring-score">
          <span class="num">{{ percent }}</span>
          <span class="unit">%</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.gauge-ring-only {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.ring-wrapper {
  position: relative;
  width: 112px;
  height: 112px;
}

.ring-svg {
  width: 100%;
  height: 100%;
  transform: rotate(-90deg);
}

.ring-bg {
  fill: none;
  stroke: rgba(255, 255, 255, 0.08);
  stroke-width: 6;
}

.ring-progress {
  fill: none;
  stroke-width: 6;
  stroke-linecap: round;
  stroke-dashoffset: 251.2;
  animation: gauge-progress-in 900ms cubic-bezier(0.22, 1, 0.36, 1) forwards;
  filter: drop-shadow(0 3px 7px rgba(39, 199, 217, 0.22));
}

.ring-content {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #69e7dc;
}

.ring-label {
  order: 0;
  margin-bottom: 3px;
  color: rgba(255, 255, 255, 0.58);
  font-size: 11px;
  font-weight: 500;
  line-height: 1;
}

.ring-score {
  display: flex;
  align-items: baseline;
}

.ring-score .num {
  font-family: Inter, Arial, sans-serif;
  font-size: 40px;
  font-weight: 700;
  color: #f8fffe;
  line-height: 1;
  letter-spacing: 0;
  font-variant-numeric: tabular-nums;
}

.ring-score .unit {
  font-size: 16px;
  font-weight: 500;
  color: rgba(105, 231, 220, 0.92);
}

@media (max-width: 360px) {
  .ring-wrapper {
    width: 106px;
    height: 106px;
  }

  .ring-score .num {
    font-size: 40px;
  }
}

@keyframes gauge-progress-in {
  to {
    stroke-dashoffset: var(--ring-offset);
  }
}

@media (prefers-reduced-motion: reduce) {
  .ring-progress {
    animation: none;
    stroke-dashoffset: var(--ring-offset);
  }
}
</style>
