<script setup lang="ts">
import { computed } from 'vue'
import { ChevronLeft, ChevronRight, CircleCheck, Share2, Sparkles } from 'lucide-vue-next'
import { useRouter } from 'vue-router'

import { useSessionStore } from '../../app/store/session'
import { recommendationProducts, type RecommendationProduct } from '../../mock/recommendationData'

const router = useRouter()
const session = useSessionStore()

if (session.recommendationProducts.length === 0) {
  session.recommendationProducts = recommendationProducts
}

const recommendations = computed(() => session.recommendationProducts)

const requirementText = computed(() => {
  const conditions = Object.keys(session.inheritedConditions).length > 0
    ? session.inheritedConditions
    : session.verificationResult?.conditions ?? {}
  const values = Object.values(conditions).flatMap((value) => Array.isArray(value) ? value : [value])
  return values.filter((value) => value !== undefined && value !== null && value !== '').slice(0, 4)
})

function selectRecommendation(product: RecommendationProduct) {
  session.selectedRecommendation = product
  session.setSelectedPriceProduct(product)
  router.push('/price-comparison')
}
</script>

<template>
  <section class="recommendation-page">
    <header class="recommendation-header">
      <button class="icon-button" type="button" aria-label="返回" @click="router.back()">
        <ChevronLeft :size="21" :stroke-width="1.8" />
      </button>
      <h1>更合适的推荐</h1>
      <button class="icon-button" type="button" aria-label="分享">
        <Share2 :size="18" :stroke-width="1.8" />
      </button>
    </header>

    <div class="ai-note">
      <Sparkles :size="17" :stroke-width="1.8" />
      <span>基于你的反馈，AI 已重新筛选更匹配的选择</span>
    </div>

    <section class="requirements-summary">
      <div class="summary-heading">
        <CircleCheck :size="17" :stroke-width="1.9" />
        <span>已继承你的需求</span>
      </div>
      <div class="summary-items">
        <span v-for="item in requirementText" :key="String(item)">{{ item }}</span>
        <span v-if="requirementText.length === 0">按原有使用需求继续筛选</span>
      </div>
    </section>

    <p class="section-note">基于相同预算与偏好，为你推荐以下更合适的选择</p>

    <main class="recommendation-list">
      <article v-for="product in recommendations" :key="product.product_id" class="recommendation-card">
        <div class="rank-label">TOP {{ product.rank }}</div>
        <div class="recommendation-image">
          <img v-if="product.image_url" :src="product.image_url" :alt="product.product_name" />
          <span v-else aria-hidden="true">{{ product.product_name.slice(0, 1) }}</span>
        </div>
        <div class="recommendation-content">
          <h2>{{ product.product_name }}</h2>
          <span class="product-type">{{ product.product_tag }}</span>
          <div class="score-line">
            <span>推荐度</span>
            <strong>{{ product.score }}%</strong>
          </div>
          <h3>{{ product.reason }}</h3>
          <p>{{ product.description }}</p>
          <div class="support-label"><CircleCheck :size="14" :stroke-width="1.9" /> 支持证据</div>
          <ul><li v-for="item in product.evidence" :key="item">{{ item }}</li></ul>
          <div class="source-line">数据来源：{{ product.source }}</div>
          <div class="card-footer">
            <span>预计到手价 <strong>¥{{ product.price }}</strong> 起</span>
            <button type="button" @click="selectRecommendation(product)">满意这款，查看全网低价 <ChevronRight :size="15" /></button>
          </div>
        </div>
      </article>
    </main>

    <footer class="recommendation-footer">
      <button type="button" class="secondary-action" @click="router.push('/conditions')">继续筛选</button>
      <button type="button" class="primary-action" @click="router.push('/conditions')">告诉 AI 新需求</button>
    </footer>
  </section>
</template>

<style scoped>
.recommendation-page {
  width: 100%;
  max-width: 430px;
  margin: 0 auto;
  padding-bottom: 34px;
  color: #e8f1fb;
  font-family: Inter, "PingFang SC", "Microsoft YaHei", sans-serif;
}
.recommendation-header { display: grid; grid-template-columns: 36px 1fr 36px; align-items: center; min-height: 56px; }
.recommendation-header h1 { margin: 0; text-align: center; font-size: 20px; font-weight: 500; }
.icon-button { width: 34px; height: 34px; display: grid; place-items: center; color: #c7d5e5; background: transparent; border: 0; }
.icon-button:last-child { justify-self: end; }
.ai-note, .requirements-summary { border: 1px solid rgba(105, 231, 220, 0.18); border-radius: 14px; }
.ai-note { display: flex; align-items: center; gap: 8px; padding: 11px 13px; color: #b7c9dd; background: rgba(67, 135, 181, 0.1); font-size: 12px; }
.ai-note svg { color: #69e7dc; flex: 0 0 auto; }
.requirements-summary { margin-top: 12px; padding: 13px; background: rgba(11, 42, 48, 0.36); }
.summary-heading, .support-label { display: flex; align-items: center; gap: 7px; color: #dcecf3; font-size: 14px; font-weight: 500; }
.summary-heading svg, .support-label svg { color: #41d2bd; }
.summary-items { display: flex; flex-wrap: wrap; gap: 7px 14px; margin-top: 10px; color: #8fa5bb; font-size: 12px; }
.summary-items span::before { content: '•'; margin-right: 5px; color: #69e7dc; }
.section-note { margin: 15px 8px 10px; color: #8498ad; font-size: 12px; text-align: center; }
.recommendation-list { display: flex; flex-direction: column; gap: 12px; }
.recommendation-card { position: relative; display: grid; grid-template-columns: 106px minmax(0, 1fr); gap: 13px; padding: 13px; overflow: hidden; background: rgba(246, 250, 255, 0.97); border: 1px solid rgba(112, 191, 218, 0.3); border-radius: 14px; color: #122237; }
.rank-label { position: absolute; top: 13px; left: 13px; padding: 4px 7px; color: #fff; background: #1f8eea; border-radius: 4px; font-size: 10px; font-weight: 600; z-index: 1; }
.recommendation-image { width: 106px; height: 106px; display: grid; place-items: center; overflow: hidden; color: #4c7aa6; background: #e7eef6; border-radius: 10px; font-size: 32px; font-weight: 500; }
.recommendation-image img { width: 100%; height: 100%; object-fit: cover; }
.recommendation-content { min-width: 0; }
.recommendation-content h2 { margin: 0; font-size: 16px; font-weight: 600; line-height: 1.3; }
.product-type { display: inline-block; margin-top: 4px; padding: 3px 6px; color: #7290aa; background: #edf3f8; border-radius: 4px; font-size: 10px; }
.score-line { display: flex; align-items: baseline; gap: 6px; margin-top: 10px; color: #16a89b; font-size: 12px; }
.score-line strong { font-size: 18px; font-weight: 700; }
.recommendation-content h3 { margin: 7px 0 0; font-size: 13px; font-weight: 600; }
.recommendation-content p, .recommendation-content li { color: #71869b; font-size: 11px; line-height: 1.5; }
.recommendation-content p { margin: 4px 0 8px; }
.recommendation-content ul { margin: 5px 0 11px; padding-left: 16px; }
.recommendation-content li { margin: 2px 0; }
.source-line { padding-top: 8px; border-top: 1px solid #e4ebf1; color: #8a9bad; font-size: 10px; line-height: 1.45; }
.card-footer { display: flex; align-items: center; justify-content: space-between; gap: 8px; padding-top: 10px; border-top: 1px solid #e4ebf1; color: #62778d; font-size: 11px; }
.card-footer > span strong { color: #192a3e; font-size: 17px; }
.card-footer button, .primary-action { display: inline-flex; align-items: center; gap: 4px; color: #fff; background: #12a89d; border: 0; border-radius: 8px; padding: 8px 10px; font-size: 11px; font-weight: 500; }
.recommendation-footer { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 16px; }
.secondary-action, .primary-action { min-height: 38px; justify-content: center; }
.secondary-action { color: #1784dd; background: transparent; border: 1px solid #4ca4ef; border-radius: 8px; font-size: 12px; }
</style>
