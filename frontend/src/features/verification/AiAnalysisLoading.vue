<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

const steps = [
  '正在从主流海量测评中提取证据链…',
  '正在交叉比对用户条件与商品规格…',
  '正在评估风险隐患与待确认项…',
  '正在智能生成置信度与最终推荐结论…'
]

const currentStep = ref(0)
const progressPercent = ref(15)
let stepTimer: number | null = null
let progressTimer: number | null = null

onMounted(() => {
  stepTimer = window.setInterval(() => {
    currentStep.value = (currentStep.value + 1) % steps.length
  }, 1200)

  progressTimer = window.setInterval(() => {
    if (progressPercent.value < 100) {
      progressPercent.value = Math.min(
        100,
        progressPercent.value + Math.floor(Math.random() * 10) + 5,
      )
    }
  }, 300)
})

onUnmounted(() => {
  if (stepTimer) clearInterval(stepTimer)
  if (progressTimer) clearInterval(progressTimer)
})
</script>

<template>
  <div class="ai-loading-container">
    <div class="ai-orb">
      <div class="orb-core"></div>
      <div class="orb-ring ring1"></div>
      <div class="orb-ring ring2"></div>
      <div class="orb-ring ring3"></div>
    </div>

    <h2 class="loading-title">AI 验真引擎分析中</h2>
    <p class="step-text">{{ steps[currentStep] }}</p>

    <!-- Progress bar -->
    <div class="progress-bar-bg">
      <div class="progress-bar-fill" :style="{ width: `${progressPercent}%` }"></div>
    </div>
    <span class="percent-label">{{ progressPercent }}%</span>
  </div>
</template>

<style scoped>
.ai-loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  background: rgba(15, 23, 42, 0.85);
  border: 1px solid rgba(56, 189, 248, 0.2);
  border-radius: 24px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(16px);
}

.ai-orb {
  position: relative;
  width: 100px;
  height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 24px;
}

.orb-core {
  width: 32px;
  height: 32px;
  background: radial-gradient(circle, rgba(105, 231, 220, 0.92), rgba(8, 74, 87, 0.96));
  border-radius: 50%;
  box-shadow: 0 8px 22px rgba(0, 0, 0, 0.24);
  animation: pulse 1.8s infinite ease-in-out;
}

.orb-ring {
  position: absolute;
  border-radius: 50%;
  border: 2px solid transparent;
}

.ring1 {
  width: 60px;
  height: 60px;
  border-top-color: #38bdf8;
  border-bottom-color: #06b6d4;
  animation: spin 1.4s linear infinite;
}

.ring2 {
  width: 80px;
  height: 80px;
  border-left-color: #3b82f6;
  border-right-color: #818cf8;
  animation: spin-reverse 2s linear infinite;
}

.ring3 {
  width: 100px;
  height: 100px;
  border-top-color: rgba(56, 189, 248, 0.4);
  animation: spin 3s linear infinite;
}

.loading-title {
  font-size: 20px;
  font-weight: 600;
  color: #f8fafc;
  margin: 0 0 8px;
  background: linear-gradient(90deg, #69e7dc, #8bb7ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.step-text {
  font-size: 14px;
  color: #94a3b8;
  margin: 0 0 24px;
  min-height: 22px;
}

.progress-bar-bg {
  width: 240px;
  height: 8px;
  background: rgba(30, 41, 59, 0.8);
  border-radius: 4px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.progress-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, rgba(35, 211, 196, 0.86), rgba(90, 167, 255, 0.8));
  border-radius: 4px;
  transition: width 0.3s ease;
}

.percent-label {
  font-size: 12px;
  color: #38bdf8;
  margin-top: 8px;
  font-weight: 500;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes spin-reverse {
  0% { transform: rotate(360deg); }
  100% { transform: rotate(0deg); }
}

@keyframes pulse {
  0%, 100% { opacity: 0.82; }
  50% { opacity: 1; }
}
</style>
