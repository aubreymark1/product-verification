<script setup lang="ts">
import { onUnmounted, ref } from 'vue'
import { ChevronRight, RotateCcw, ShieldCheck } from 'lucide-vue-next'
import { useSessionStore } from '../../app/store/session'

const emit = defineEmits<{
  click: []
}>()

const session = useSessionStore()
const isAnalyzing = ref(false)
const analysisStep = ref(0)
let analysisTimer: number | null = null
const analysisSteps = [
  '正在继承你的原有需求',
  '正在排除不符合预算的商品',
  '正在匹配更适合 FPS 的鼠标',
  '正在聚合替代商品的口碑证据',
  '正在生成更合适的推荐',
]

function startRecommendation() {
  if (isAnalyzing.value) return
  isAnalyzing.value = true
  analysisStep.value = 0
  session.inheritedConditions = session.verificationResult?.conditions ?? {}

  analysisTimer = window.setInterval(() => {
    if (analysisStep.value < analysisSteps.length - 1) analysisStep.value += 1
  }, 560)

  window.setTimeout(() => {
    if (analysisTimer !== null) window.clearInterval(analysisTimer)
    analysisTimer = null
    emit('click')
  }, 2800)
}

onUnmounted(() => {
  if (analysisTimer !== null) window.clearInterval(analysisTimer)
})
</script>

<template>
  <div class="rerecommend-card-container">
    <button class="rerecommend-card" type="button" :disabled="isAnalyzing" @click="startRecommendation">
      <div class="left-group">
        <div class="refresh-circle">
          <RotateCcw :size="18" :stroke-width="1.8" />
        </div>
        <div class="text-group">
          <div v-if="!isAnalyzing" class="title-row">
            <span class="title-text">继续帮我找更合适的</span>
            <ChevronRight class="arrow" :size="15" :stroke-width="1.8" />
          </div>
          <span v-if="!isAnalyzing" class="sub-text">基于需求重新筛选，发现更多好物</span>
          <span v-else class="analysis-text">{{ analysisSteps[analysisStep] }}</span>
        </div>
      </div>
    </button>

    <!-- AI Footer Disclaimer -->
    <div class="ai-footer-disclaimer">
      <ShieldCheck :size="13" :stroke-width="1.8" />
      <span>AI 结论基于公开内容，仅供参考</span>
    </div>
  </div>
</template>

<style scoped>
.rerecommend-card-container {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.rerecommend-card {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(13, 24, 38, 0.62);
  border: 1px solid rgba(90, 167, 255, 0.14);
  border-radius: 12px;
  padding: 15px 12px;
  cursor: pointer;
  text-align: left;
  transition: all 0.2s ease;
}

.rerecommend-card:hover {
  background: rgba(18, 31, 49, 0.72);
  border-color: rgba(90, 167, 255, 0.22);
}

.rerecommend-card:disabled {
  cursor: wait;
  opacity: 0.86;
}

.left-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.refresh-circle {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: transparent;
  border: 0;
  color: #38bdf8;
  display: flex;
  align-items: center;
  justify-content: center;
}

.text-group {
  display: flex;
  flex-direction: column;
}

.title-row {
  display: flex;
  align-items: center;
  gap: 4px;
}

.title-text {
  font-size: 15px;
  font-weight: 500;
  color: #ffffff;
}

.arrow {
  color: #38bdf8;
}

.sub-text {
  font-size: 11px;
  font-weight: 400;
  color: rgba(255, 255, 255, 0.5);
  margin-top: 6px;
}

.analysis-text {
  color: rgba(255, 255, 255, 0.78);
  font-size: 12px;
  font-weight: 400;
}

.ai-footer-disclaimer {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  font-size: 11px;
  font-weight: 400;
  color: rgba(255, 255, 255, 0.4);
  padding: 8px 0 16px;
}

</style>
