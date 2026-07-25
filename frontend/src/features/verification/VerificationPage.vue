<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

import StatusMessage from '../../components/common/StatusMessage.vue'
import EvidenceCard from '../../components/evidence/EvidenceCard.vue'
import EvidenceDetailModal from '../../components/evidence/EvidenceDetailModal.vue'
import RequirementTags from '../conditions/RequirementTags.vue'
import RecommendationGauge from './RecommendationGauge.vue'
import ProductHeroCard from './ProductHeroCard.vue'
import MultiChannelPurchase from './MultiChannelPurchase.vue'
import ReRecommendLoop from './ReRecommendLoop.vue'

import { useSessionStore } from '../../app/store/session'
import { api } from '../../services/api'
import type { Evidence } from '../../types/api'

const router = useRouter()
const session = useSessionStore()
const evidence = ref<Evidence | null>(null)
const evidenceLoading = ref(false)
const error = ref('')

async function rerunRecommendation() {
  if (!session.verificationResult || !session.selectedProduct) return
  try {
    const result = await api.rerunRecommendation({
      video_id: session.videoId,
      product_id: session.selectedProduct.product_id,
      category_id: session.categoryId,
      previous_result_id: session.verificationResult.result_id,
      dissatisfaction_reasons: [],
      dissatisfaction_note: '',
      inherit_previous_needs: true,
      conditions_patch: {},
      raw_query: '',
    })
    session.setProduct(result.product)
    session.setVerificationResult(result)
  } catch (err) {
    error.value = err instanceof Error ? err.message : '再推荐失败'
  }
}

async function openEvidence(id: string) {
  evidenceLoading.value = true
  error.value = ''
  try {
    evidence.value = await api.getEvidence(id)
  } catch (err) {
    error.value = err instanceof Error ? err.message : '证据加载失败'
  } finally {
    evidenceLoading.value = false
  }
}

async function addComparison() {
  if (!session.selectedProduct) return
  try {
    await api.addComparison({
      product_id: session.selectedProduct.product_id,
      category_id: session.categoryId,
      result_id: session.verificationResult?.result_id,
    })
    await router.push('/comparison')
  } catch (err) {
    error.value = err instanceof Error ? err.message : '加入横评失败'
  }
}
</script>

<template>
  <section class="verification-page-shell">
    <!-- Header -->
    <div class="page-top-header">
      <button class="back-link" @click="router.push('/conditions')">&lt; 返回设置</button>
      <h1 class="nav-title">验真结果</h1>
      <button class="share-btn">🔗</button>
    </div>

    <!-- Empty State -->
    <StatusMessage
      v-if="!session.verificationResult"
      type="empty"
      message="还没有可展示的验真结果，请从视频页或条件配置页开始流程。"
    />

    <!-- Main Results View -->
    <div v-else class="results-wrapper">
      <!-- Top Row: Gauge + Hero Card -->
      <div class="top-hero-row">
        <RecommendationGauge
          :score="session.verificationResult.recommendation_score"
          :summary="session.verificationResult.summary"
          class="hero-gauge"
        />
        <ProductHeroCard
          :product="session.verificationResult.product || session.selectedProduct"
          class="hero-product"
        />
      </div>

      <!-- My Requirements Tags -->
      <RequirementTags
        :conditions="session.verificationResult.conditions"
      />

      <!-- Overall AI Conclusion Banner -->
      <div class="conclusion-banner">
        <div class="shield-icon">🛡️</div>
        <div class="conclusion-text">
          当前证据支持<strong class="highlight-text">{{ session.verificationResult.product?.product_name || '该商品' }}</strong>较好满足你的需求，整体推荐购买。
        </div>
      </div>

      <!-- Evidence Accordion Cards (Risk, Support, Uncertain) -->
      <div class="evidence-group">
        <!-- 🔴 Risk Evidence -->
        <EvidenceCard
          type="risk"
          title="风险证据"
          :items="session.verificationResult.risks"
          @select-evidence="openEvidence"
        />

        <!-- 🟢 Support Evidence -->
        <EvidenceCard
          type="support"
          title="支持证据"
          :items="session.verificationResult.support"
          @select-evidence="openEvidence"
        />

        <!-- 🟡 Uncertain Items -->
        <EvidenceCard
          type="uncertain"
          title="待确认项"
          :items="session.verificationResult.uncertain"
          @select-evidence="openEvidence"
        />
      </div>

      <!-- Actions Bar: Comparison Button -->
      <div class="comparison-bar">
        <button class="comparison-action-btn" @click="addComparison">
          <span>📊 加入多商品横评（占位）</span>
        </button>
      </div>

      <!-- Multi-channel Purchase Banner -->
      <MultiChannelPurchase />

      <!-- Re-recommendation Loop Banner -->
      <ReRecommendLoop @click="rerunRecommendation" />

      <!-- Bottom Disclaimer -->
      <div class="disclaimer-footer">
        <span>🛡️ AI 结论基于公开网络内容与测评数据，仅供参考</span>
      </div>
    </div>

    <!-- Error Banner -->
    <StatusMessage v-if="error" type="error" :message="error" />

    <!-- Evidence Loading Modal -->
    <div v-if="evidenceLoading" class="modal-loading-backdrop">
      <div class="loading-box">正在加载证据详情…</div>
    </div>

    <!-- Evidence Detail Modal -->
    <EvidenceDetailModal
      :evidence="evidence"
      @close="evidence = null"
    />
  </section>
</template>

<style scoped>
.verification-page-shell {
  max-width: 640px;
  margin: 0 auto;
  padding-bottom: 40px;
}

.page-top-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 18px;
}

.back-link {
  background: none;
  border: none;
  color: #94a3b8;
  font-size: 14px;
  cursor: pointer;
}

.nav-title {
  font-size: 18px;
  font-weight: 700;
  color: #f8fafc;
  margin: 0;
}

.share-btn {
  background: rgba(30, 41, 59, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  width: 32px;
  height: 32px;
  color: #94a3b8;
  cursor: pointer;
}

.results-wrapper {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.top-hero-row {
  display: grid;
  grid-template-columns: 180px 1fr;
  gap: 14px;
}

@media (max-width: 580px) {
  .top-hero-row {
    grid-template-columns: 1fr;
  }
}

.conclusion-banner {
  display: flex;
  align-items: center;
  gap: 12px;
  background: rgba(6, 182, 212, 0.1);
  border: 1px solid rgba(6, 182, 212, 0.35);
  border-radius: 16px;
  padding: 14px 18px;
  backdrop-filter: blur(10px);
}

.shield-icon {
  font-size: 24px;
  flex-shrink: 0;
}

.conclusion-text {
  font-size: 14px;
  color: #e2e8f0;
  line-height: 1.5;
}

.highlight-text {
  color: #38bdf8;
}

.evidence-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.comparison-bar {
  display: flex;
  justify-content: center;
}

.comparison-action-btn {
  width: 100%;
  padding: 12px;
  background: rgba(30, 41, 59, 0.6);
  border: 1px dashed rgba(56, 189, 248, 0.3);
  border-radius: 14px;
  color: #38bdf8;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.comparison-action-btn:hover {
  background: rgba(56, 189, 248, 0.15);
  border-color: #38bdf8;
}

.disclaimer-footer {
  text-align: center;
  font-size: 12px;
  color: #64748b;
  margin-top: 10px;
}

.modal-loading-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(10, 15, 29, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 99;
}

.loading-box {
  background: #0f172a;
  color: #38bdf8;
  padding: 16px 24px;
  border-radius: 12px;
  border: 1px solid rgba(56, 189, 248, 0.3);
}
</style>
