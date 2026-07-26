<script setup lang="ts">
import { computed } from 'vue'
import { ChevronLeft, ChevronRight, CircleCheck, Share2, Sparkles, Target } from 'lucide-vue-next'
import { useRouter } from 'vue-router'

import { useSessionStore } from '../../app/store/session'
import { presentationScore } from './presentationScore'

const router = useRouter()
const session = useSessionStore()

interface DisplayRecommendation {
  product_id: string
  product_name: string
  image_url: string | null
  product_tag: string
  score: number
  reason: string
  description: string
  evidence: string[]
  source: string
  price: string
  rank: number
  reviewSummary: string
  demoPriceNote: string
}

const recommendations = computed<DisplayRecommendation[]>(() => {
  const result = session.verificationResult
  const product = result?.product || session.selectedProduct
  if (!product) return []
  const evidence = [...(result?.support ?? []), ...(result?.risks ?? [])]
  const sourceIds = evidence.flatMap((item) => item.source_ids)
  const demo = result?.demo_insights
  const lowestOffer = demo?.price_offers.length
    ? demo.price_offers.reduce((lowest, offer) => offer.price < lowest.price ? offer : lowest)
    : null
  const averageRating = demo?.reviews.length
    ? demo.reviews.reduce((total, review) => total + review.rating, 0) / demo.reviews.length
    : null
  return [{
    product_id: product.product_id,
    product_name: product.product_name,
    image_url: product.image_url,
    product_tag: session.identifyResult?.category_name || '商品',
    score: Math.round(presentationScore(result) * 100),
    reason: sourceIds.length
      ? (result?.summary || '基于当前识别结果与需求进行评估')
      : '演示匹配参考：该候选商品仍需可信来源完成验真。',
    description: result?.change_summary || '暂无额外说明',
    evidence: evidence.map((item) => item.claim),
    source: sourceIds.length ? sourceIds.join(', ') : '暂无可信来源',
    price: lowestOffer ? lowestOffer.price.toFixed(2) : '待确认',
    rank: 1,
    reviewSummary: averageRating === null ? '' : `用户口碑 ${averageRating.toFixed(1)} / 5（${demo?.reviews.length} 条演示评价）`,
    demoPriceNote: lowestOffer ? `${lowestOffer.channel_name} · 演示价格` : '',
  }]
})

const requirementText = computed(() => {
  const conditions = Object.keys(session.inheritedConditions).length > 0
    ? session.inheritedConditions
    : session.verificationResult?.conditions ?? {}
  const values = Object.values(conditions).flatMap((value) => Array.isArray(value) ? value : [value])
  return values.filter((value) => value !== undefined && value !== null && value !== '').slice(0, 4)
})

function selectRecommendation(product: DisplayRecommendation) {
  const selected = session.verificationResult?.product || session.selectedProduct
  if (selected) session.setSelectedPriceProduct(selected)
  router.push('/price-comparison')
}
</script>

<template>
  <section class="smartphone-app-shell recommendation-demo">
    <div class="phone-frame">
      <div class="dynamic-island"></div>

      <div class="status-bar">
        <span>12:51</span>
        <div class="status-right">
          <span>5G</span>
          <span>73%</span>
        </div>
      </div>

      <div class="recommendation-screen">
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
        <div class="recommendation-top">
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
            <div v-if="product.reviewSummary" class="review-reference">
              <span>{{ product.reviewSummary }}</span>
              <em>Mock</em>
            </div>
            <h3><Target :size="16" :stroke-width="1.8" /> <span>{{ product.reason }}</span></h3>
            <p>{{ product.description }}</p>
          </div>
        </div>

        <div class="recommendation-details">
          <div class="support-label"><CircleCheck :size="14" :stroke-width="1.9" /> 支持证据</div>
          <ul><li v-for="item in product.evidence" :key="item">{{ item }}</li></ul>
          <div v-if="session.verificationResult?.demo_insights?.reviews.length" class="review-evidence-preview">
            <div class="review-evidence-preview__heading">
              <span>平台评论参考</span>
              <em>演示数据</em>
            </div>
            <p>{{ session.verificationResult.demo_insights.reviews[0].content }}</p>
          </div>
          <div class="source-line">
            <span>数据来源：{{ product.source }}</span>
            <span v-if="product.demoPriceNote" class="demo-source-note">{{ product.demoPriceNote }}</span>
          </div>
          <div class="card-footer">
            <span>预计到手价 <strong>¥{{ product.price }}</strong> 起</span>
            <button type="button" @click="selectRecommendation(product)">满意这款，查看全网低价 <ChevronRight :size="15" /></button>
          </div>
        </div>
      </article>
    </main>

    <footer class="recommendation-footer">
      <button type="button" class="secondary-action" @click="router.push('/conditions')">继续筛选</button>
    </footer>
        </section>
      </div>
    </div>
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
.review-reference { display: flex; align-items: center; flex-wrap: wrap; gap: 5px; margin-top: 6px; color: #617a91; font-size: 10px; }
.review-reference em, .demo-source-note { color: #a16b00; font-style: normal; }
.review-reference em { padding: 2px 5px; background: #fff1cf; border-radius: 999px; }
.recommendation-content h3 { margin: 7px 0 0; font-size: 13px; font-weight: 600; }
.recommendation-content p, .recommendation-content li { color: #71869b; font-size: 11px; line-height: 1.5; }
.recommendation-content p { margin: 4px 0 8px; }
.recommendation-content ul { margin: 5px 0 11px; padding-left: 16px; }
.recommendation-content li { margin: 2px 0; }
.review-evidence-preview { margin: 7px 0 10px; padding: 8px 9px; background: #f3f8fb; border: 1px solid #dbe8ef; border-radius: 8px; }
.review-evidence-preview__heading { display: flex; align-items: center; justify-content: space-between; color: #59758d; font-size: 10px; }
.review-evidence-preview__heading em { color: #9a6800; font-style: normal; }
.review-evidence-preview p { margin: 5px 0 0; color: #637b91; font-size: 11px; line-height: 1.5; }
.source-line { display: flex; flex-direction: column; gap: 3px; padding-top: 8px; border-top: 1px solid #e4ebf1; color: #8a9bad; font-size: 10px; line-height: 1.45; }
.card-footer { display: flex; align-items: center; justify-content: space-between; gap: 8px; padding-top: 10px; border-top: 1px solid #e4ebf1; color: #62778d; font-size: 11px; }
.card-footer > span strong { color: #192a3e; font-size: 17px; }
.card-footer button, .primary-action { display: inline-flex; align-items: center; gap: 4px; color: #fff; background: #12a89d; border: 0; border-radius: 8px; padding: 8px 10px; font-size: 11px; font-weight: 500; }
.recommendation-footer { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 16px; }
.secondary-action, .primary-action { min-height: 38px; justify-content: center; }
.secondary-action { color: #1784dd; background: transparent; border: 1px solid #4ca4ef; border-radius: 8px; font-size: 12px; }

:global(.app-shell:has(.recommendation-demo) .topbar) {
  display: none;
}

:global(.page-shell:has(.recommendation-demo)) {
  max-width: none;
  min-height: 100dvh;
  padding: 0;
  background: #040711;
}

.smartphone-app-shell {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100dvh;
  padding: 16px 0;
  font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
  background:
    radial-gradient(circle at 50% 12%, rgba(56, 189, 248, 0.16), transparent 28%),
    #040711;
}

.phone-frame {
  position: relative;
  display: flex;
  flex-direction: column;
  width: 390px;
  height: 844px;
  overflow: hidden;
  background: #000000;
  border: 8px solid #1e293b;
  border-radius: 40px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.8);
}

.dynamic-island {
  position: absolute;
  top: 10px;
  left: 50%;
  z-index: 99;
  width: 110px;
  height: 26px;
  background: #000000;
  border-radius: 18px;
  transform: translateX(-50%);
}

.status-bar {
  position: absolute;
  top: 12px;
  right: 24px;
  left: 24px;
  z-index: 98;
  display: flex;
  justify-content: space-between;
  color: #ffffff;
  font-size: 12px;
  font-weight: 600;
}

.status-right {
  display: flex;
  gap: 8px;
}

.recommendation-screen {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
  background:
    radial-gradient(circle at 50% -4%, rgba(35, 211, 196, 0.16), transparent 30%),
    linear-gradient(180deg, #07101c 0%, #050914 42%, #040711 100%);
}

.recommendation-page {
  position: relative;
  width: 100%;
  height: 100%;
  max-width: none;
  margin: 0;
  padding: 0 14px;
  overflow-y: auto;
  scrollbar-width: none;
}

.recommendation-page::-webkit-scrollbar {
  display: none;
}

.recommendation-header {
  position: sticky;
  top: 0;
  z-index: 80;
  display: grid;
  grid-template-columns: 36px 1fr 36px;
  align-items: center;
  margin: 0 -14px;
  padding: 44px 14px 0;
  min-height: 98px;
  background:
    linear-gradient(
      180deg,
      rgba(4, 7, 17, 0.99) 0%,
      rgba(5, 9, 20, 0.98) 58%,
      rgba(5, 9, 20, 0.82) 100%
    );
  backdrop-filter: blur(14px);
}

.recommendation-header::after {
  position: absolute;
  right: 0;
  bottom: -34px;
  left: 0;
  height: 34px;
  pointer-events: none;
  background: linear-gradient(180deg, rgba(5, 9, 20, 0.62), rgba(5, 9, 20, 0));
  content: "";
}

.recommendation-header h1 {
  color: #f8fafc;
  font-size: 18px;
  font-weight: 500;
  line-height: 1.25;
}

.icon-button {
  display: grid;
  width: 34px;
  height: 34px;
  place-items: center;
  color: #d7e3f0;
  background: transparent;
  border: 0;
}

.icon-button:last-child {
  justify-self: end;
}

.ai-note,
.requirements-summary {
  border-color: rgba(105, 231, 220, 0.18);
  background: rgba(15, 23, 42, 0.72);
}

.ai-note {
  color: #b7c9dd;
}

.ai-note svg {
  color: #69e7dc;
}

.requirements-summary {
  background: rgba(11, 42, 48, 0.36);
}

.summary-heading,
.support-label {
  color: #dcecf3;
}

.summary-heading svg,
.support-label svg {
  color: #41d2bd;
}

.summary-items {
  color: #8fa5bb;
}

.section-note {
  color: #8498ad;
}

.recommendation-card {
  color: #e8f1fb;
  background: rgba(15, 23, 42, 0.74);
  border-color: rgba(132, 112, 255, 0.2);
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.22);
}

.rank-label {
  color: #f8f7ff;
  background: #6659c7;
}

.recommendation-image {
  color: #b8a3ff;
  background: rgba(132, 112, 255, 0.1);
  border: 1px solid rgba(132, 112, 255, 0.14);
}

.recommendation-content h2,
.recommendation-content h3 {
  color: #ffffff;
}

.product-type {
  color: #b8a3ff;
  background: rgba(132, 112, 255, 0.11);
}

.score-line {
  color: #69e7dc;
}

.recommendation-content p,
.recommendation-content li {
  color: #8da0b7;
}

.source-line,
.card-footer {
  color: #8092a8;
  border-color: rgba(255, 255, 255, 0.08);
}

.card-footer > span strong {
  color: #ffc58b;
}

.card-footer button,
.primary-action {
  color: #061426;
  background: linear-gradient(135deg, #69e7dc, #8ec1ff);
  box-shadow: 0 8px 18px rgba(35, 211, 196, 0.16);
}

.recommendation-footer {
  position: sticky;
  bottom: 0;
  z-index: 50;
  margin: 16px -14px 0;
  grid-template-columns: 1fr;
  padding: 12px 14px calc(12px + env(safe-area-inset-bottom));
  background: rgba(4, 7, 17, 0.96);
  border-top: 1px solid rgba(105, 231, 220, 0.12);
  box-shadow: 0 -12px 28px rgba(0, 0, 0, 0.34);
  backdrop-filter: blur(14px);
}

.secondary-action {
  color: #8ec1ff;
  background: transparent;
  border-color: rgba(142, 193, 255, 0.42);
}

.recommendation-card {
  display: block;
}

.recommendation-top {
  display: grid;
  grid-template-columns: 90px minmax(0, 1fr);
  gap: 13px;
  align-items: start;
}

.recommendation-image {
  width: 90px;
  height: 120px;
  border-radius: 11px;
}

.recommendation-details {
  margin-top: 14px;
}

.recommendation-content h3 {
  display: flex;
  gap: 6px;
  align-items: center;
}

.recommendation-content h3 svg {
  flex: 0 0 auto;
  color: #69e7dc;
}

.recommendation-details .support-label {
  margin-top: 0;
}

.recommendation-details .source-line {
  margin-top: 10px;
}

.recommendation-details .card-footer {
  margin-top: 10px;
}

/* Keep the card hierarchy compact: identity, recommendation, then supporting detail. */
.recommendation-card {
  font-size: 11px;
  line-height: 1.45;
}

.recommendation-content h2 {
  font-size: 15px;
  font-weight: 600;
  line-height: 1.3;
}

.product-type {
  font-size: 10px;
  line-height: 1.2;
}

.score-line {
  margin-top: 9px;
  font-size: 11px;
  line-height: 1.2;
}

.score-line strong {
  font-size: 18px;
  line-height: 1;
}

.recommendation-content h3 {
  margin-top: 8px;
  font-size: 13px;
  font-weight: 600;
  line-height: 1.35;
}

.recommendation-content p {
  margin: 5px 0 0;
  font-size: 11px;
  line-height: 1.45;
}

.recommendation-details .support-label {
  gap: 6px;
  color: #a5b5c8;
  font-size: 11px;
  font-weight: 500;
  line-height: 1.3;
}

.recommendation-details .support-label svg {
  width: 13px;
  height: 13px;
  color: #69e7dc;
}

.recommendation-details ul {
  margin: 6px 0 0;
  padding-left: 14px;
}

.recommendation-details li {
  margin: 2px 0;
  color: #8295ab;
  font-size: 10px;
  line-height: 1.4;
}

.recommendation-details .source-line {
  margin-top: 9px;
  padding-top: 8px;
  color: #74879d;
  font-size: 10px;
  line-height: 1.35;
}

.recommendation-details .card-footer {
  gap: 8px;
  margin-top: 9px;
  padding-top: 9px;
  color: #a5b5c8;
  font-size: 11px;
  line-height: 1.3;
}

.recommendation-details .card-footer > span strong {
  font-size: 17px;
  line-height: 1;
}

.recommendation-details .card-footer button {
  font-size: 11px;
  line-height: 1.25;
}

@media (max-width: 430px) {
  .smartphone-app-shell {
    padding: 0;
  }

  .phone-frame {
    width: 100vw;
    height: 100dvh;
    border: 0;
    border-radius: 0;
  }
}

@media (max-width: 370px) {
  .recommendation-top {
    grid-template-columns: 78px minmax(0, 1fr);
    gap: 10px;
  }

  .recommendation-image {
    width: 78px;
    height: 104px;
  }

  .card-footer {
    flex-wrap: wrap;
  }

  .card-footer button {
    flex: 1 1 100%;
    justify-content: center;
  }
}


/* Douyin theme: Douyin light recommendation page. */
:global(.page-shell:has(.recommendation-demo)) {
  background: #ececee;
}

.smartphone-app-shell {
  background: #ececee;
}

.phone-frame {
  color: #161823;
  background: #ffffff;
  border-color: #161823;
  box-shadow: 0 20px 50px rgba(22, 24, 35, 0.2);
}

.status-bar { color: #161823; }

.recommendation-screen {
  background: #f7f7f8;
}

.recommendation-page { color: #161823; }

.recommendation-header {
  background: rgba(255, 255, 255, 0.96);
  border-bottom: 1px solid #ececee;
  box-shadow: 0 4px 14px rgba(22, 24, 35, 0.04);
}

.recommendation-header::after { display: none; }
.recommendation-header h1 { color: #161823; font-weight: 600; }
.icon-button { color: #34353b; }

.ai-note,
.requirements-summary {
  background: #ffffff;
  border-color: #ececee;
  box-shadow: 0 2px 10px rgba(22, 24, 35, 0.04);
}

.ai-note { color: #616269; }
.ai-note svg { color: #fe2c55; }

.requirements-summary {
  background: #edfbfa;
  border-color: rgba(0, 207, 200, 0.2);
}

.summary-heading,
.support-label { color: #24252b; }

.summary-heading svg,
.support-label svg { color: #00a69f; }

.summary-items { color: #616269; }
.summary-items span::before { color: #00a69f; }
.section-note { color: #8a8b91; }

.recommendation-card {
  color: #161823;
  background: #ffffff;
  border-color: #e7e7e9;
  box-shadow: 0 3px 14px rgba(22, 24, 35, 0.06);
}

.rank-label {
  color: #ffffff;
  background: #fe2c55;
}

.recommendation-image {
  color: #7a7b81;
  background: #f1f1f2;
  border-color: #e5e5e7;
}

.recommendation-content h2,
.recommendation-content h3 { color: #161823; }

.product-type {
  color: #64656b;
  background: #f1f1f2;
}

.score-line { color: #fe2c55; }
.review-reference { color: #8a8b91; }

.review-reference em {
  color: #b06f00;
  background: #fff7e8;
}

.recommendation-content h3 svg { color: #00a69f; }

.recommendation-content p,
.recommendation-content li,
.recommendation-details li { color: #66676d; }

.recommendation-details .support-label { color: #34353b; }
.recommendation-details .support-label svg { color: #00a69f; }

.review-evidence-preview {
  background: #f7f7f8;
  border-color: #ececee;
}

.review-evidence-preview__heading { color: #8a8b91; }
.review-evidence-preview__heading em { color: #fe2c55; }
.review-evidence-preview p { color: #5f6066; }

.source-line,
.card-footer,
.recommendation-details .source-line,
.recommendation-details .card-footer {
  color: #8a8b91;
  border-color: #ececee;
}

.demo-source-note { color: #b06f00; }
.card-footer > span strong,
.recommendation-details .card-footer > span strong { color: #fe2c55; }

.card-footer button,
.primary-action {
  color: #ffffff;
  background: #fe2c55;
  box-shadow: none;
}

.recommendation-footer {
  background: rgba(255, 255, 255, 0.97);
  border-top-color: #ececee;
  box-shadow: 0 -8px 22px rgba(22, 24, 35, 0.08);
}

.secondary-action {
  color: #161823;
  background: #ffffff;
  border-color: #d9d9dc;
}

.secondary-action:hover { background: #f5f5f6; }
</style>
