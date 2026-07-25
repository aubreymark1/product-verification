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
        <!-- Background Track -->
        <circle cx="50" cy="50" r="40" class="ring-bg" />
        <!-- Progress Arc -->
        <circle
          cx="50"
          cy="50"
          r="40"
          class="ring-progress"
          :stroke-dasharray="251.2"
          :stroke-dashoffset="251.2 * (1 - percent / 100)"
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
  width: 90px;
  height: 90px;
}

.ring-svg {
  width: 100%;
  height: 100%;
  transform: rotate(-90deg);
}

.ring-bg {
  fill: none;
  stroke: rgba(255, 255, 255, 0.08);
  stroke-width: 8;
}

.ring-progress {
  fill: none;
  stroke: #06b6d4;
  stroke-width: 8;
  stroke-linecap: round;
  transition: stroke-dashoffset 0.8s ease-in-out;
  filter: drop-shadow(0 0 6px rgba(6, 182, 212, 0.6));
}

.ring-content {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #38bdf8;
}

.ring-label {
  font-size: 10px;
  color: #38bdf8;
  font-weight: 500;
  margin-bottom: -2px;
}

.ring-score {
  display: flex;
  align-items: baseline;
}

.ring-score .num {
  font-size: 22px;
  font-weight: 800;
  color: #38bdf8;
  line-height: 1;
}

.ring-score .unit {
  font-size: 11px;
  font-weight: 700;
  color: #38bdf8;
}
</style>
