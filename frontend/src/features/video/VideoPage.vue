<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'

import VerifyPillButton from '../../components/common/VerifyPillButton.vue'
import BottomDrawer from '../../components/common/BottomDrawer.vue'
import RecommendationGauge from '../verification/RecommendationGauge.vue'
import ProductHeroCard from '../verification/ProductHeroCard.vue'
import RequirementTags from '../conditions/RequirementTags.vue'
import EvidenceCard from '../../components/evidence/EvidenceCard.vue'
import EvidenceDetailModal from '../../components/evidence/EvidenceDetailModal.vue'
import MultiChannelPurchase from '../verification/MultiChannelPurchase.vue'
import ReRecommendLoop from '../verification/ReRecommendLoop.vue'

import { useSessionStore } from '../../app/store/session'
import { api } from '../../services/api'
import type { Evidence, VerificationResult } from '../../types/api'

const router = useRouter()
const session = useSessionStore()

const videoSrc = '/mock/videos/mouse-demo.mp4'
const videoRef = ref<HTMLVideoElement | null>(null)
const isPaused = ref(false)

// Drawer state (1: Target Confirmation, 2: Requirements Input, 3: AI Analysis, 4: Results)
const showDrawer = ref(false)
const drawerStep = ref(1)

// Selected product candidate state
const selectedCandidateId = ref('product_gpro')
const rawQueryText = ref('')
const isRecording = ref(false)

// Options selections
const selectedBudget = ref('<300')
const selectedConnection = ref('无线')

// AI Analysis Loading steps
const aiProgress = ref(68)
const aiStepIndex = ref(0)
let aiTimer: number | null = null

// Verification Results & Evidence Modal
const verificationResult = ref<VerificationResult | null>(null)
const selectedEvidence = ref<Evidence | null>(null)

onMounted(() => {
  session.videoId = 'video_demo'
  session.categoryId = 'mouse'
  session.setProduct({
    product_id: 'product_gpro',
    product_name: '轻量化无线游戏鼠标 G Pro',
    confidence: 0.92,
    image_url: null,
  })
})

onUnmounted(() => {
  if (aiTimer) clearInterval(aiTimer)
})

function togglePlay() {
  if (!videoRef.value) return
  if (videoRef.value.paused) {
    videoRef.value.play().catch(() => {})
  } else {
    videoRef.value.pause()
  }
}

function handlePlay() {
  isPaused.value = false
}

function handlePause() {
  isPaused.value = true
}

function openVerificationDrawer() {
  if (videoRef.value && !videoRef.value.paused) {
    videoRef.value.pause()
  }
  drawerStep.value = 1
  showDrawer.value = true
}

function confirmProductStep() {
  drawerStep.value = 2
}

let voiceTimer: number | null = null

function toggleVoiceRecording() {
  if (isRecording.value) {
    if (voiceTimer) clearInterval(voiceTimer)
    isRecording.value = false
    return
  }

  isRecording.value = true
  rawQueryText.value = ''

  const fullText = '预算300元以内，主要玩FPS，希望无线、轻量、低延迟。'
  let idx = 0
  voiceTimer = window.setInterval(() => {
    if (idx < fullText.length) {
      rawQueryText.value += fullText[idx]
      idx++
    } else {
      if (voiceTimer) clearInterval(voiceTimer)
      isRecording.value = false
      selectedBudget.value = '<300'
      selectedConnection.value = '无线'
    }
  }, 60)
}

async function startAiAnalysis() {
  drawerStep.value = 3
  aiProgress.value = 25
  aiStepIndex.value = 0

  aiTimer = window.setInterval(() => {
    if (aiProgress.value < 90) {
      aiProgress.value += 20
      if (aiStepIndex.value < 4) aiStepIndex.value++
    }
  }, 300)

  try {
    const res = await api.runVerification({
      video_id: session.videoId,
      product_id: selectedCandidateId.value,
      category_id: 'mouse',
      conditions: {
        budget: selectedBudget.value,
        connection: selectedConnection.value,
      },
      raw_query: rawQueryText.value,
    })

    setTimeout(() => {
      if (aiTimer) clearInterval(aiTimer)
      verificationResult.value = res
      session.setVerificationResult(res)
      drawerStep.value = 4
    }, 1300)
  } catch (err) {
    console.error(err)
    drawerStep.value = 4
  }
}

async function openEvidenceDetail(id: string) {
  try {
    selectedEvidence.value = await api.getEvidence(id)
  } catch (err) {
    console.error(err)
  }
}
</script>

<template>
  <div class="smartphone-app-shell">
    <!-- iPhone 15 Pro Smartphone Frame Container -->
    <div class="phone-frame">
      <!-- Dynamic Island Top Notch -->
      <div class="dynamic-island"></div>

      <!-- Top Status Bar -->
      <div class="status-bar">
        <span>12:51</span>
        <div class="status-right">
          <span>5G</span>
          <span>73%</span>
        </div>
      </div>

      <!-- Video Screen -->
      <div class="video-feed-screen" @click="togglePlay">
        <!-- Top Nav -->
        <div class="tiktok-top-bar" @click.stop>
          <div class="nav-tabs">
            <span>关注</span>
            <span class="active">推荐</span>
          </div>
        </div>

        <!-- Video Element -->
        <video
          ref="videoRef"
          :src="videoSrc"
          autoplay
          muted
          loop
          playsinline
          preload="auto"
          class="phone-video-player"
          @play="handlePlay"
          @pause="handlePause"
        ></video>

        <!-- Bounding Rings around Target -->
        <div class="target-bounding-overlay" @click.stop="openVerificationDrawer">
          <div class="clean-target-ring">
            <span class="target-dot"></span>
            <span class="target-name">无线游戏鼠标</span>
          </div>
        </div>

        <!-- Floating Pill Button -->
        <div class="floating-pill-position" @click.stop="openVerificationDrawer">
          <VerifyPillButton />
        </div>

        <!-- Right TikTok Sidebar -->
        <div class="tiktok-right-sidebar" @click.stop>
          <div class="sidebar-item">
            <span class="icon">❤️</span>
            <span class="count">143.7万</span>
          </div>
          <div class="sidebar-item">
            <span class="icon">💬</span>
            <span class="count">1.4万</span>
          </div>
          <div class="sidebar-item">
            <span class="icon">⭐</span>
            <span class="count">3.4万</span>
          </div>
        </div>

        <!-- Bottom Navigation Bar -->
        <div class="tiktok-bottom-nav" @click.stop>
          <span class="active">首页</span>
          <span>朋友</span>
          <span class="plus-btn">+</span>
          <span>消息</span>
          <span>我</span>
        </div>
      </div>

      <!-- Bottom Sheet Drawer Modal -->
      <BottomDrawer
        :show="showDrawer"
        :title="drawerStep === 1 ? '确认目标商品' : drawerStep === 2 ? '补充使用需求' : drawerStep === 3 ? 'AI 分析中' : '验真结果'"
        @close="showDrawer = false"
      >
        <!-- STEP 1: 确认目标商品 -->
        <div v-if="drawerStep === 1" class="drawer-step">
          <div class="section-subtitle">根据视频内容自动匹配候选目标:</div>

          <div class="candidate-cards-list">
            <div
              class="cand-card-item"
              :class="{ selected: selectedCandidateId === 'product_gpro' }"
              @click="selectedCandidateId = 'product_gpro'"
            >
              <div class="card-left-img"></div>
              <div class="card-right-info">
                <div class="info-top-row">
                  <span class="product-title-text">轻量化无线游戏鼠标 G Pro</span>
                  <span class="confidence-badge">置信度 92%</span>
                </div>
                <div class="product-sub-spec">约63g / RGB灯效 / 极低延迟</div>
              </div>
            </div>

            <div
              class="cand-card-item"
              :class="{ selected: selectedCandidateId === 'product_viper' }"
              @click="selectedCandidateId = 'product_viper'"
            >
              <div class="card-left-img"></div>
              <div class="card-right-info">
                <div class="info-top-row">
                  <span class="product-title-text">双模无线电竞鼠标</span>
                  <span class="confidence-badge">置信度 78%</span>
                </div>
                <div class="product-sub-spec">长续航 / 可编程侧键</div>
              </div>
            </div>
          </div>

          <button class="restrained-primary-btn" @click="confirmProductStep">
            <span class="btn-main-text">确认并进入下一步</span>
          </button>
        </div>

        <!-- STEP 2: 补充使用需求 (Douyin Native Restrained Aesthetic) -->
        <div v-else-if="drawerStep === 2" class="drawer-step step-2-native">
          <!-- 5. 已识别商品卡片 (二级容器 #121824，边框 rgba(255,255,255,0.08)) -->
          <div class="identified-product-card">
            <div class="product-thumb"></div>
            <div class="product-meta">
              <span class="meta-label">已识别商品</span>
              <span class="meta-title">轻量化无线游戏鼠标 G Pro</span>
            </div>
          </div>

          <!-- 单行需求输入框（限定名词提示：用途/预算/重量/材质...） -->
          <div class="single-line-input-bar" :class="{ focused: isRecording }">
            <input
              type="text"
              v-model="rawQueryText"
              placeholder="用途/预算/重量/材质..."
              class="single-input-field"
            />
            <button
              type="button"
              class="mic-circle-wrapper"
              :class="{ active: isRecording }"
              @click.stop="toggleVoiceRecording"
              :title="isRecording ? '点击停止语音输入' : '点击开始语音输入'"
            >
              <!-- Icon when recording: Stop Square -->
              <svg v-if="isRecording" width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
                <rect x="5" y="5" width="14" height="14" rx="2" />
              </svg>
              <!-- Icon when idle: Microphone -->
              <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3z"></path>
                <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
                <line x1="12" y1="19" x2="12" y2="22"></line>
              </svg>
              <!-- Natural breathing wave indicator -->
              <span v-if="isRecording" class="natural-wave-ring"></span>
            </button>
          </div>

          <!-- 开始验真 主按钮 (已删除预计8秒生成结果字样) -->
          <button class="restrained-primary-btn" @click="startAiAnalysis">
            <span class="btn-main-text">开始验真</span>
          </button>
        </div>

        <!-- STEP 3: AI 比对分析中 -->
        <div v-else-if="drawerStep === 3" class="drawer-step loading">
          <div class="progress-linear-bar">
            <div class="fill" :style="{ width: `${aiProgress}%` }"></div>
          </div>
          <span class="progress-text">AI 综合分析中 {{ aiProgress }}%</span>

          <div class="clean-checklist">
            <div class="check-row" :class="{ active: aiStepIndex >= 0 }">
              <span class="dot"></span>
              <span>检索海量测评与专业跑分数据</span>
            </div>
            <div class="check-row" :class="{ active: aiStepIndex >= 1 }">
              <span class="dot"></span>
              <span>分析真实用户使用反馈与论坛口碑</span>
            </div>
            <div class="check-row" :class="{ active: aiStepIndex >= 2 }">
              <span class="dot"></span>
              <span>交叉比对预算与核心配置需求</span>
            </div>
            <div class="check-row" :class="{ active: aiStepIndex >= 3 }">
              <span class="dot"></span>
              <span>生成可解释置信度与证据链条</span>
            </div>
          </div>
        </div>

        <!-- STEP 4: 验真结果 -->
        <div v-else-if="drawerStep === 4" class="drawer-step result">
          <div class="top-hero-block">
            <div class="top-hero-row">
              <RecommendationGauge :score="verificationResult?.confidence || 0.82" />
              <ProductHeroCard :product="verificationResult?.product || session.selectedProduct" categoryName="鼠标/电竞游戏鼠标" />
            </div>

            <div class="summary-single-line">
              <span class="sparkle">✨</span>
              <span class="summary-text">综合评价较优，适合大部分玩家</span>
            </div>
          </div>

          <RequirementTags :conditions="verificationResult?.conditions" />

          <div class="conclusion-banner">
            <span class="check-icon">✓</span>
            <span class="banner-text">当前证据支持<strong>该鼠标能较好满足你的需求</strong>，整体推荐购买。</span>
          </div>

          <div class="evidence-clean-list">
            <EvidenceCard type="risk" title="风险证据" :items="verificationResult?.risks || []" @select-evidence="openEvidenceDetail" />
            <EvidenceCard type="support" title="支持证据" :items="verificationResult?.support || []" @select-evidence="openEvidenceDetail" />
            <EvidenceCard type="uncertain" title="待确认项" :items="verificationResult?.uncertain || []" @select-evidence="openEvidenceDetail" />
          </div>

          <MultiChannelPurchase />
          <ReRecommendLoop @click="drawerStep = 2" />
        </div>
      </BottomDrawer>

      <EvidenceDetailModal :evidence="selectedEvidence" @close="selectedEvidence = null" />
    </div>
  </div>
</template>

<style scoped>
.smartphone-app-shell {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #040711;
  padding: 16px 0;
  font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
}

.phone-frame {
  position: relative;
  width: 390px;
  height: 844px;
  border-radius: 40px;
  background: #000000;
  border: 8px solid #1e293b;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.8);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.dynamic-island {
  position: absolute;
  top: 10px;
  left: 50%;
  transform: translateX(-50%);
  width: 110px;
  height: 26px;
  background: #000000;
  border-radius: 18px;
  z-index: 99;
}

.status-bar {
  position: absolute;
  top: 12px;
  left: 24px;
  right: 24px;
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  font-weight: 600;
  color: #ffffff;
  z-index: 98;
}

.status-right {
  display: flex;
  gap: 8px;
}

.video-feed-screen {
  position: relative;
  width: 100%;
  height: 100%;
  background: #000000;
}

.tiktok-top-bar {
  position: absolute;
  top: 46px;
  left: 0;
  right: 0;
  display: flex;
  justify-content: center;
  z-index: 20;
}

.nav-tabs {
  display: flex;
  gap: 16px;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
}

.nav-tabs .active {
  color: #ffffff;
  font-weight: 700;
}

.phone-video-player {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.target-bounding-overlay {
  position: absolute;
  top: 42%;
  left: 26%;
  z-index: 15;
  cursor: pointer;
}

.clean-target-ring {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 14px;
  background: rgba(15, 23, 42, 0.8);
  border: 1px solid rgba(56, 189, 248, 0.5);
  color: #38bdf8;
  font-size: 11px;
  font-weight: 600;
  backdrop-filter: blur(8px);
}

.target-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #38bdf8;
}

.floating-pill-position {
  position: absolute;
  bottom: 100px;
  right: 18px;
  z-index: 20;
}

.tiktok-right-sidebar {
  position: absolute;
  right: 12px;
  bottom: 120px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  color: white;
  z-index: 20;
  font-size: 11px;
  align-items: center;
}

.sidebar-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.sidebar-item .icon {
  font-size: 22px;
}

.tiktok-bottom-nav {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 52px;
  background: #000000;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  justify-content: space-around;
  align-items: center;
  color: #64748b;
  font-size: 12px;
  z-index: 20;
}

.tiktok-bottom-nav .active {
  color: white;
  font-weight: 600;
}

.plus-btn {
  background: #ffffff;
  color: #000;
  font-weight: 700;
  padding: 2px 10px;
  border-radius: 6px;
}

.drawer-step {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

/* STEP 1 Styles */
.section-subtitle {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 2px;
}

.candidate-cards-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.cand-card-item {
  display: flex;
  align-items: center;
  gap: 12px;
  background: #121824;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  padding: 12px 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.cand-card-item.selected {
  border-color: rgba(56, 189, 248, 0.5);
  background: rgba(56, 189, 248, 0.08);
}

.card-left-img {
  width: 44px;
  height: 44px;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.05);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.img-icon {
  font-size: 22px;
}

.card-right-info {
  display: flex;
  flex-direction: column;
  gap: 3px;
  flex: 1;
}

.info-top-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.product-title-text {
  font-size: 14px;
  font-weight: 600;
  color: #ffffff;
}

.confidence-badge {
  font-size: 12px;
  color: #38bdf8;
  font-weight: 500;
}

.product-sub-spec {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
}

/* STEP 2: Douyin Native Aesthetic Styles */
.step-2-native {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

/* 4 & 5. 已识别商品卡片 */
.identified-product-card {
  display: flex;
  align-items: center;
  gap: 12px;
  background: #121824;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  padding: 12px 14px;
}

.product-thumb {
  width: 40px;
  height: 40px;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.06);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.thumb-icon {
  font-size: 20px;
}

.product-meta {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.meta-label {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
  font-weight: 400;
}

.meta-title {
  font-size: 14px;
  font-weight: 600;
  color: #ffffff;
}

/* 单行需求输入框 */
.single-line-input-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 48px;
  background: #121824;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  padding: 0 8px 0 14px;
  transition: border-color 0.25s ease, background 0.25s ease;
}

.single-line-input-bar.focused {
  border-color: rgba(56, 189, 248, 0.35);
  background: rgba(18, 24, 36, 0.95);
}

.single-input-field {
  flex: 1;
  background: transparent;
  border: none;
  color: #ffffff;
  font-size: 13px;
  outline: none;
}

.single-input-field::placeholder {
  color: rgba(255, 255, 255, 0.45);
}

.mic-circle-wrapper {
  position: relative;
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.08);
  border: none;
  color: rgba(255, 255, 255, 0.65);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  outline: none;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  flex-shrink: 0;
}

.mic-circle-wrapper:hover {
  background: rgba(255, 255, 255, 0.14);
  color: #ffffff;
}

.mic-circle-wrapper:active {
  transform: scale(0.92);
}

.mic-circle-wrapper.active {
  background: rgba(56, 189, 248, 0.22);
  color: #38bdf8;
  box-shadow: 0 0 12px rgba(56, 189, 248, 0.3);
}

.natural-wave-ring {
  position: absolute;
  inset: -3px;
  border-radius: 50%;
  border: 1.5px solid rgba(56, 189, 248, 0.5);
  animation: naturalBreath 1.6s cubic-bezier(0.4, 0, 0.2, 1) infinite;
  pointer-events: none;
}

@keyframes naturalBreath {
  0% {
    transform: scale(0.96);
    opacity: 0.8;
  }
  50% {
    transform: scale(1.16);
    opacity: 0.25;
  }
  100% {
    transform: scale(0.96);
    opacity: 0.8;
  }
}

/* 13-15. 克制的高质感主按钮 (高度 56px, 圆角 16px) */
.restrained-primary-btn {
  width: 100%;
  height: 56px;
  border-radius: 10px;
  background: linear-gradient(135deg, #1d4ed8, #2563eb);
  border: none;
  color: #ffffff;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
  cursor: pointer;
  transition: opacity 0.15s ease;
  margin-top: 6px;
}

.restrained-primary-btn:hover {
  opacity: 0.94;
}

.restrained-primary-btn:active {
  transform: scale(0.99);
}

.btn-main-text {
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.btn-sub-hint {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.7);
  font-weight: 400;
}

/* STEP 3 & STEP 4 */
.progress-linear-bar {
  height: 4px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 2px;
  overflow: hidden;
}

.progress-linear-bar .fill {
  height: 100%;
  background: #38bdf8;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 12px;
  color: #38bdf8;
  text-align: center;
  font-weight: 600;
}

.clean-checklist {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 6px;
}

.check-row {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
}

.check-row.active {
  color: #ffffff;
}

.check-row .dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.3);
}

.check-row.active .dot {
  background: #38bdf8;
}

.top-hero-block {
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: 100%;
}

.top-hero-row {
  display: flex;
  align-items: center;
  gap: 16px;
}

.summary-single-line {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.6);
  text-align: left;
  padding-left: 2px;
  white-space: nowrap;
}

.summary-single-line .sparkle {
  font-size: 10px;
}

.conclusion-banner {
  display: flex;
  align-items: center;
  gap: 10px;
  background: rgba(16, 185, 129, 0.08);
  border: 1px solid rgba(16, 185, 129, 0.35);
  border-radius: 8px;
  padding: 12px 14px;
  color: #ffffff;
  font-size: 13px;
  line-height: 1.4;
}

.conclusion-banner .check-icon {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: #10b981;
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 12px;
  flex-shrink: 0;
}

.conclusion-banner strong {
  color: #38bdf8;
}

.evidence-clean-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
</style>
