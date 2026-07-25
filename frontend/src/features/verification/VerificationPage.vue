<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  BarChart3,
  ChevronLeft,
  Share2,
  ShieldCheck,
  Sparkles,
} from 'lucide-vue-next'

import StatusMessage from '../../components/common/StatusMessage.vue'
import EvidenceSearchHeading from '../../components/evidence/EvidenceSearchHeading.vue'
import EvidenceSection from '../../mock/EvidenceSection.vue'
import EvidenceSourceDetail from '../../mock/EvidenceSourceDetail.vue'
import RequirementTags from '../conditions/RequirementTags.vue'
import RecommendationGauge from './RecommendationGauge.vue'
import ProductHeroCard from './ProductHeroCard.vue'
import MultiChannelPurchase from './MultiChannelPurchase.vue'
import ReRecommendLoop from './ReRecommendLoop.vue'
import VerificationSummary from './VerificationSummary.vue'

import { useSessionStore } from '../../app/store/session'
import { api } from '../../services/api'
import {
  mockEvidenceGroups,
  type EvidenceItem,
} from '../../mock/evidenceData'

const router = useRouter()
const session = useSessionStore()

const error = ref('')

/**
 * 默认显示第一条风险证据的来源详情。
 * 如果 Mock 数据为空，则安全回退为 null。
 */
const selectedEvidence = ref<EvidenceItem | null>(
  mockEvidenceGroups.find((group) => group.type === 'risk')?.items[0] ?? null,
)

/**
 * 点击证据条目后，切换下方的来源详情。
 */
function handleEvidenceSelect(item: EvidenceItem) {
  selectedEvidence.value = item
}

/**
 * 加入横评。
 *
 * 暂时保留现有后端接口。
 * 接口不可用时仍然进入横评页，避免前端演示流程被阻断。
 */
async function addComparison() {
  if (!session.selectedProduct) {
    error.value = '暂未识别到可加入横评的商品'
    return
  }

  error.value = ''

  try {
    await api.addComparison({
      product_id: session.selectedProduct.product_id,
      category_id: session.categoryId,
      result_id: session.verificationResult?.result_id,
    })
  } catch (err) {
    console.warn('横评接口暂不可用，使用前端演示模式继续：', err)
  }

  await router.push('/comparison')
}
</script>

<template>
  <section class="verification-page-shell">
    <!-- 顶部导航 -->
    <div class="page-top-header">
      <button
        type="button"
        class="back-link"
        @click="router.push('/conditions')"
      >
        <ChevronLeft :size="17" :stroke-width="1.8" />
        <span>返回设置</span>
      </button>

      <h1 class="nav-title">验真结果</h1>

      <button
        type="button"
        class="share-btn"
        aria-label="分享验真结果"
      >
        <Share2 :size="17" :stroke-width="1.8" />
      </button>
    </div>

    <!-- 空状态 -->
    <StatusMessage
      v-if="!session.verificationResult"
      type="empty"
      message="还没有可展示的验真结果，请从视频页或条件配置页开始流程。"
    />

    <!-- 验真结果主体 -->
    <div v-else class="results-wrapper">
      <!-- 推荐度与商品信息 -->
      <div class="top-hero-row">
        <RecommendationGauge
          :score="session.verificationResult.confidence"
          :summary="session.verificationResult.summary"
          class="hero-gauge"
        />

        <ProductHeroCard
          :product="
            session.verificationResult.product ||
            session.selectedProduct
          "
          class="hero-product"
        />
      </div>

      <!-- 综合评价 -->
      <div class="overall-rating-row">
        <Sparkles :size="14" :stroke-width="1.8" />
        <span>综合评价较优，适合大部分玩家</span>
      </div>

      <!-- 用户需求标签 -->
      <RequirementTags
        :conditions="session.verificationResult.conditions"
      />

      <!-- 验真总结 -->
      <VerificationSummary
        :product-name="
          session.verificationResult.product?.product_name ||
          session.selectedProduct?.product_name ||
          '该商品'
        "
      />

      <!-- 前端 Mock 证据区域 -->
      <div class="evidence-group">
        <EvidenceSearchHeading />

        <EvidenceSection
          v-for="group in mockEvidenceGroups"
          :key="group.type"
          :group="group"
          :default-expanded="true"
          @select="handleEvidenceSelect"
        />

        <!-- 点击证据后显示对应的来源详情 -->
        <EvidenceSourceDetail
          :item="selectedEvidence"
        />
      </div>

      <!-- 加入横评 -->
      <div class="comparison-bar">
        <button
          type="button"
          class="comparison-action-btn"
          @click="addComparison"
        >
          <BarChart3 :size="17" :stroke-width="1.8" />
          <span>加入多商品横评</span>
        </button>
      </div>

      <!-- 全网低价 -->
      <MultiChannelPurchase />

      <!-- 重新推荐 -->
      <ReRecommendLoop @click="router.push('/recommendations')" />

      <!-- 免责声明 -->
      <div class="disclaimer-footer">
        <ShieldCheck :size="15" :stroke-width="1.8" />
        <span>AI 结论基于公开网络内容与测评数据，仅供参考</span>
      </div>
    </div>

    <!-- 错误提示 -->
    <StatusMessage
      v-if="error"
      type="error"
      :message="error"
    />
  </section>
</template>

<style scoped>
.verification-page-shell {
  width: 100%;
  max-width: 430px;
  margin: 0 auto;
  padding-bottom: 44px;

  font-family:
    "Inter",
    "PingFang SC",
    "Microsoft YaHei",
    "Noto Sans SC",
    "Helvetica Neue",
    Arial,
    sans-serif;

  scrollbar-width: none;
}

.verification-page-shell::-webkit-scrollbar {
  display: none;
}

:global(html),
:global(body),
:global(.page-shell) {
  scrollbar-width: none;
}

:global(html::-webkit-scrollbar),
:global(body::-webkit-scrollbar),
:global(.page-shell::-webkit-scrollbar) {
  display: none;
}

/* 顶部导航 */

.page-top-header {
  display: grid;
  grid-template-columns: minmax(84px, 1fr) auto minmax(36px, 1fr);
  align-items: center;
  margin-bottom: 12px;
}

.back-link {
  display: inline-flex;
  align-items: center;
  gap: 2px;

  padding: 0;

  font-size: 14px;
  color: #94a3b8;

  background: none;
  border: none;
  cursor: pointer;
}

.nav-title {
  margin: 0;

  font-size: 22px;
  font-weight: 500;
  line-height: 1.3;
  letter-spacing: 0;
  color: #f8fafc;
}

.share-btn {
  display: grid;
  width: 32px;
  height: 32px;
  place-items: center;
  justify-self: end;

  color: #94a3b8;

  background: rgba(30, 41, 59, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  cursor: pointer;
}

/* 结果区域 */

.results-wrapper {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

/* 推荐度与商品卡 */

.top-hero-row {
  display: grid;
  grid-template-columns: 128px minmax(0, 1fr);
  column-gap: 14px;
  align-items: center;

  width: 100%;
  max-width: 100%;
  min-height: 132px;
  padding: 0;
  overflow: hidden;

  background: transparent;
  border: 0;
  border-radius: 0;
  box-shadow: none;
}

.hero-gauge,
.hero-product {
  min-width: 0;
}

/* 综合评价 */

.overall-rating-row {
  display: flex;
  gap: 6px;
  align-items: center;

  height: 24px;
  margin-top: -6px;

  font-size: 12px;
  font-weight: 400;
  color: rgba(255, 255, 255, 0.55);
}

.overall-rating-row svg {
  flex-shrink: 0;
  color: #69e7dc;
}

/* 证据区域 */

.evidence-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 6px;
}

/* 横评入口 */

.comparison-bar {
  display: flex;
  justify-content: center;
  margin-top: 12px;
}

.comparison-action-btn {
  display: inline-flex;
  gap: 7px;
  align-items: center;
  justify-content: center;

  width: 100%;
  min-height: 42px;
  padding: 10px 12px;

  font-size: 12px;
  font-weight: 400;
  color: #8ec1ff;

  background: rgba(19, 31, 45, 0.68);
  border: 1px solid rgba(90, 167, 255, 0.18);
  border-radius: 12px;
  cursor: pointer;

  transition:
    background-color 180ms ease,
    border-color 180ms ease;
}

.comparison-action-btn:hover {
  background: rgba(90, 167, 255, 0.11);
  border-color: rgba(90, 167, 255, 0.28);
}

.comparison-action-btn:active {
  background: rgba(90, 167, 255, 0.15);
}

/* 底部说明 */

.disclaimer-footer {
  display: flex;
  gap: 5px;
  align-items: center;
  justify-content: center;

  margin-top: 10px;

  font-size: 12px;
  color: #64748b;
  text-align: center;
}

.disclaimer-footer svg {
  flex-shrink: 0;
}

/* 响应式 */

@media (max-width: 580px) {
  .top-hero-row {
    grid-template-columns: 128px minmax(0, 1fr);
    column-gap: 14px;
    min-height: 132px;
  }
}

@media (max-width: 390px) {
  .verification-page-shell {
    max-width: 100%;
  }

  .page-top-header {
    grid-template-columns: minmax(76px, 1fr) auto minmax(34px, 1fr);
  }

  .back-link {
    font-size: 13px;
  }

  .nav-title {
    font-size: 22px;
  }

  .results-wrapper {
    gap: 16px;
  }
}

@media (max-width: 370px) {
  .top-hero-row {
    grid-template-columns: 118px minmax(0, 1fr);
    column-gap: 10px;
  }
}
</style>
