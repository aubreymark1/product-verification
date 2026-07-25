<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import {
  BadgeCheck,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  Clock3,
  Filter,
  Gift,
  RefreshCw,
  Share2,
  ShieldCheck,
  ShoppingBag,
  SlidersHorizontal,
  Store,
  Truck,
  X,
} from 'lucide-vue-next'
import { useRouter } from 'vue-router'

import { useSessionStore } from '../../app/store/session'
import { api } from '../../services/api'

const router = useRouter()
const session = useSessionStore()

interface DisplayChannel {
  id: string
  name: string
  tag: string
  score: string
  price: string
  originalPrice: string
  offer: string
  shipping: string[]
  arrival: string
  warranty: string
  stars: number
  sales: string
  accent: string
}

const channels = ref<DisplayChannel[]>([])

async function loadChannels() {
  const productId = session.selectedProduct?.product_id
  if (!productId) {
    channels.value = []
    return
  }
  try {
    const result = await api.getPurchaseChannels(productId)
    channels.value = result.map((channel, index) => ({
      id: channel.channel_id,
      name: channel.channel_name,
      tag: channel.note,
      score: '待评估',
      price: '待确认',
      originalPrice: '',
      offer: channel.availability === 'available' ? '可购买' : '待确认',
      shipping: [channel.note || '配送信息待确认'],
      arrival: '待确认',
      warranty: '以渠道说明为准',
      stars: 0,
      sales: '—',
      accent: index === 0 ? 'purple' : 'blue',
    }))
  } catch (error) {
    channels.value = []
    console.warn('比价渠道加载失败', error)
  }
}

onMounted(() => { void loadChannels() })
watch(() => session.selectedProduct?.product_id, () => { void loadChannels() })
const lowestChannel = computed(() => channels.value[0] ?? null)
const selectedProduct = computed(
  () => session.selectedPriceProduct || session.selectedRecommendation || session.selectedProduct,
)
const productName = computed(() => selectedProduct.value?.product_name || '待识别商品')
const selectedChannel = ref<DisplayChannel | null>(null)
const showPurchaseConfirm = ref(false)
const purchaseTriggered = ref(false)

function openPurchase(channel: DisplayChannel | null) {
  if (!channel) return

  selectedChannel.value = channel
  purchaseTriggered.value = false
  showPurchaseConfirm.value = true
}

function confirmPurchase() {
  purchaseTriggered.value = true
}
</script>

<template>
  <section class="smartphone-app-shell low-price-demo">
    <div class="phone-frame">
      <div class="dynamic-island"></div>

      <div class="status-bar">
        <span>12:51</span>
        <div class="status-right">
          <span>5G</span>
          <span>73%</span>
        </div>
      </div>

      <div class="price-screen">
        <section class="low-price-page">
          <header class="price-header">
            <button class="icon-button" type="button" aria-label="返回" @click="router.back()">
              <ChevronLeft :size="22" :stroke-width="1.9" />
            </button>
            <h1>查看全网低价</h1>
            <button class="icon-button" type="button" aria-label="分享">
              <Share2 :size="18" :stroke-width="1.8" />
            </button>
          </header>

          <div class="price-status">
            <span class="status-main">
              <ShieldCheck :size="15" :stroke-width="1.9" />
              AI 实时比价 · 价格每日更新
            </span>
            <span class="updated">
              <RefreshCw :size="13" :stroke-width="1.8" />
              05-26 09:41
            </span>
          </div>

          <section class="product-price-summary">
            <div class="product-price-image" aria-hidden="true">
              <ShoppingBag :size="36" :stroke-width="1.7" />
            </div>

            <div class="product-copy">
              <h2>
                {{ productName }}
                <span class="ai-recommended">AI 推荐</span>
              </h2>
              <div class="product-tags">
                <span>轻量约 63g</span>
                <span>HERO 传感器</span>
                <span>16000 DPI</span>
                <span>可编程按键</span>
                <span>RGB 灯效</span>
                <span>2.4G 无线连接</span>
              </div>
              <p>已有 12.8 万人对该商品进行了比价</p>
            </div>
          </section>

          <nav class="price-filters" aria-label="价格筛选">
            <button class="filter-active" type="button">
              <BadgeCheck :size="15" :stroke-width="1.9" />
              低价优先
            </button>
            <button type="button">
              <Truck :size="15" :stroke-width="1.8" />
              包邮优先
            </button>
            <button type="button">
              发货地
              <ChevronDown :size="14" :stroke-width="1.8" />
            </button>
            <button type="button">
              筛选
              <Filter :size="15" :stroke-width="1.8" />
            </button>
          </nav>

          <main class="channel-list">
            <article
              v-for="(channel, index) in channels"
              :key="channel.id"
              class="channel-card"
              :class="[`channel-card--${channel.accent}`, { featured: index === 0 }]"
            >
              <span v-if="index === 0" class="current-badge">当前低价</span>

              <div class="channel-top">
                <div class="channel-mark" aria-hidden="true">
                  <ShoppingBag v-if="index < 2" :size="22" :stroke-width="1.8" />
                  <Store v-else :size="22" :stroke-width="1.8" />
                </div>

                <div class="channel-main">
                  <div class="channel-heading">
                    <h2>{{ channel.name }}</h2>
                    <span class="score-pill">推荐 {{ channel.score }}</span>
                  </div>

                  <div class="price-row">
                    <strong>￥{{ channel.price }}</strong>
                    <span class="offer-chip">{{ channel.offer }}</span>
                    <del>￥{{ channel.originalPrice }}</del>
                  </div>

                  <div class="service-line">
                    {{ channel.shipping.join(' | ') }}
                  </div>
                </div>

                <div class="buy-column">
                  <button type="button" @click="openPurchase(channel)">去购买</button>
                  <span>月销 {{ channel.sales }}</span>
                </div>
              </div>

              <div class="channel-meta">
                <span>
                  <Clock3 :size="15" :stroke-width="1.8" />
                  <small>到手价</small>
                  <b>￥{{ channel.price }}</b>
                </span>
                <span>
                  <Truck :size="16" :stroke-width="1.8" />
                  <small>到货时效</small>
                  <b>{{ channel.arrival }}</b>
                </span>
                <span>
                  <ShieldCheck :size="16" :stroke-width="1.8" />
                  <small>质保服务</small>
                  <b>{{ channel.warranty }}</b>
                </span>
                <span>
                  <SlidersHorizontal :size="16" :stroke-width="1.8" />
                  <small>综合推荐</small>
                  <b class="stars" aria-label="综合推荐星级">
                    <i
                      v-for="star in 5"
                      :key="star"
                      :class="{ filled: star <= channel.stars }"
                    >★</i>
                  </b>
                </span>
              </div>
            </article>
          </main>

          <div class="price-benefits">
            <span>
              <SlidersHorizontal :size="17" :stroke-width="1.8" />
              <b>比价说明</b>
              <small>监控 100+ 渠道价格</small>
            </span>
            <span>
              <Gift :size="17" :stroke-width="1.8" />
              <b>价格保护</b>
              <small>买贵赔差价</small>
            </span>
            <span>
              <ShieldCheck :size="17" :stroke-width="1.8" />
              <b>安全保障</b>
              <small>正品与售后保障</small>
            </span>
          </div>

          <footer class="price-footer">
            <div>
              <span>当前最低价</span>
              <strong>￥{{ lowestChannel?.price || '259.00' }}</strong>
              <small>已为你节省 ￥40.00</small>
            </div>
            <button type="button" @click="openPurchase(lowestChannel)">
              去低价购买
              <ChevronRight :size="18" :stroke-width="2" />
            </button>
          </footer>

          <div
            v-if="showPurchaseConfirm"
            class="purchase-backdrop"
            @click.self="showPurchaseConfirm = false"
          >
            <section class="purchase-sheet" aria-modal="true" role="dialog">
              <button
                class="purchase-close"
                type="button"
                aria-label="关闭"
                @click="showPurchaseConfirm = false"
              >
                <X :size="18" :stroke-width="1.9" />
              </button>
              <h2>即将前往该渠道购买</h2>
              <p v-if="selectedChannel">当前到手价：￥{{ selectedChannel.price }}</p>
              <p v-if="selectedChannel">渠道：{{ selectedChannel.name }}</p>
              <p v-if="purchaseTriggered" class="purchase-success">演示模式：购买渠道跳转已触发</p>
              <div v-else class="purchase-actions">
                <button type="button" class="cancel-button" @click="showPurchaseConfirm = false">
                  取消
                </button>
                <button type="button" class="continue-button" @click="confirmPurchase">
                  继续前往
                </button>
              </div>
            </section>
          </div>
        </section>
      </div>
    </div>
  </section>
</template>

<style scoped>
:global(.app-shell:has(.low-price-demo) .topbar) {
  display: none;
}

:global(.page-shell:has(.low-price-demo)) {
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

.price-screen {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
  background:
    radial-gradient(circle at 50% -4%, rgba(35, 211, 196, 0.16), transparent 30%),
    linear-gradient(180deg, #07101c 0%, #050914 42%, #040711 100%);
}

.low-price-page {
  position: relative;
  width: 100%;
  height: 100%;
  padding: 0 14px;
  overflow-y: auto;
  color: #e8f1fb;
  scrollbar-width: none;
}

.low-price-page::-webkit-scrollbar {
  display: none;
}

.price-header {
  position: sticky;
  top: 0;
  z-index: 80;
  display: grid;
  grid-template-columns: 36px 1fr 36px;
  align-items: center;
  margin: 0 -14px 0;
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

.price-header::after {
  position: absolute;
  right: 0;
  bottom: -34px;
  left: 0;
  height: 34px;
  pointer-events: none;
  background:
    linear-gradient(
      180deg,
      rgba(5, 9, 20, 0.62) 0%,
      rgba(5, 9, 20, 0.28) 48%,
      rgba(5, 9, 20, 0) 100%
    );
  content: "";
}

.price-header h1 {
  margin: 0;
  color: #f8fafc;
  font-size: 18px;
  font-weight: 500;
  line-height: 1.25;
  text-align: center;
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

.price-status {
  display: flex;
  gap: 8px;
  align-items: center;
  min-height: 36px;
  padding: 9px 11px;
  color: #9fb0c4;
  background: rgba(15, 23, 42, 0.72);
  border: 1px solid rgba(105, 231, 220, 0.1);
  border-radius: 10px;
  font-size: 12px;
}

.status-main,
.updated {
  display: inline-flex;
  gap: 5px;
  align-items: center;
  min-width: 0;
  white-space: nowrap;
}

.status-main {
  overflow: hidden;
  text-overflow: ellipsis;
}

.status-main svg,
.updated svg {
  flex: 0 0 auto;
  color: #69e7dc;
}

.updated {
  margin-left: auto;
  color: #7f91a8;
  font-size: 11px;
}

.product-price-summary {
  display: grid;
  grid-template-columns: 98px minmax(0, 1fr);
  gap: 12px;
  align-items: center;
  min-height: 128px;
  margin-top: 12px;
  padding: 14px;
  background:
    linear-gradient(145deg, rgba(15, 23, 42, 0.92), rgba(11, 42, 48, 0.54));
  border: 1px solid rgba(105, 231, 220, 0.16);
  border-radius: 14px;
  box-shadow: 0 14px 30px rgba(0, 0, 0, 0.24);
}

.product-price-image {
  display: grid;
  width: 94px;
  height: 94px;
  place-items: center;
  color: #69e7dc;
  background:
    radial-gradient(circle at 50% 40%, rgba(105, 231, 220, 0.18), transparent 55%),
    rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(105, 231, 220, 0.14);
  border-radius: 12px;
}

.product-copy {
  min-width: 0;
}

.product-copy h2 {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  align-items: center;
  margin: 0 0 8px;
  color: #ffffff;
  font-size: 15px;
  font-weight: 600;
  line-height: 1.34;
}

.ai-recommended {
  flex: 0 0 auto;
  padding: 3px 7px;
  color: #69e7dc;
  background: rgba(35, 211, 196, 0.12);
  border: 1px solid rgba(105, 231, 220, 0.18);
  border-radius: 6px;
  font-size: 10px;
  font-weight: 600;
}

.product-tags {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 5px 10px;
  color: #91a4bb;
  font-size: 11px;
  line-height: 1.35;
}

.product-tags span::before {
  margin-right: 4px;
  color: #69e7dc;
  content: "·";
}

.product-copy p {
  margin: 9px 0 0;
  color: #7f91a8;
  font-size: 11px;
}

.price-filters {
  display: grid;
  grid-template-columns: repeat(4, auto);
  gap: 8px;
  align-items: center;
  justify-content: space-between;
  margin: 15px 0 10px;
}

.price-filters button {
  display: inline-flex;
  gap: 4px;
  align-items: center;
  min-height: 28px;
  padding: 0;
  color: #8597ad;
  white-space: nowrap;
  background: transparent;
  border: 0;
  font-size: 11px;
}

.price-filters .filter-active {
  color: #69e7dc;
  font-weight: 600;
}

.channel-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.channel-card {
  position: relative;
  padding: 16px 13px 14px;
  overflow: hidden;
  background: rgba(15, 23, 42, 0.74);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 13px;
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.22);
}

.channel-card.featured {
  border-color: rgba(105, 231, 220, 0.45);
  box-shadow:
    0 0 0 1px rgba(105, 231, 220, 0.08),
    0 16px 32px rgba(0, 0, 0, 0.25);
}

.current-badge {
  position: absolute;
  top: 0;
  left: 0;
  padding: 6px 12px 7px;
  color: #031014;
  background: #69e7dc;
  border-bottom-right-radius: 12px;
  font-size: 11px;
  font-weight: 600;
}

.channel-top {
  display: grid;
  grid-template-columns: 48px minmax(0, 1fr) 70px;
  gap: 10px;
  align-items: center;
  margin-top: 2px;
}

.featured .channel-top {
  margin-top: 14px;
}

.channel-mark {
  display: grid;
  width: 48px;
  height: 48px;
  place-items: center;
  color: #69e7dc;
  background: rgba(35, 211, 196, 0.1);
  border: 1px solid rgba(105, 231, 220, 0.15);
  border-radius: 10px;
}

.channel-card--blue .channel-mark {
  color: #8ec1ff;
  background: rgba(90, 167, 255, 0.1);
  border-color: rgba(90, 167, 255, 0.16);
}

.channel-card--violet .channel-mark {
  color: #b8a3ff;
  background: rgba(132, 112, 255, 0.1);
  border-color: rgba(132, 112, 255, 0.16);
}

.channel-main {
  min-width: 0;
}

.channel-heading {
  display: flex;
  gap: 7px;
  align-items: center;
}

.channel-heading h2 {
  min-width: 0;
  margin: 0;
  overflow: hidden;
  color: #ffffff;
  font-size: 14px;
  font-weight: 600;
  line-height: 1.25;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.score-pill {
  flex: 0 0 auto;
  padding: 4px 6px;
  color: #69e7dc;
  background: rgba(35, 211, 196, 0.11);
  border-radius: 6px;
  font-size: 10px;
  font-weight: 500;
}

.channel-card--blue .score-pill {
  color: #8ec1ff;
  background: rgba(90, 167, 255, 0.11);
}

.channel-card--violet .score-pill {
  color: #b8a3ff;
  background: rgba(132, 112, 255, 0.11);
}

.price-row {
  display: flex;
  flex-wrap: wrap;
  gap: 7px;
  align-items: baseline;
  margin-top: 10px;
}

.price-row strong {
  color: #ffffff;
  font-size: 19px;
  font-weight: 600;
  line-height: 1;
}

.price-row del {
  color: #64748b;
  font-size: 11px;
}

.offer-chip {
  padding: 3px 6px;
  color: #ffc58b;
  white-space: nowrap;
  background: rgba(255, 164, 48, 0.1);
  border: 1px solid rgba(255, 164, 48, 0.16);
  border-radius: 5px;
  font-size: 10px;
}

.service-line {
  margin-top: 9px;
  overflow: hidden;
  color: #8496ad;
  font-size: 11px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.buy-column {
  display: flex;
  flex-direction: column;
  gap: 7px;
  align-items: center;
  justify-content: center;
}

.buy-column button {
  width: 64px;
  min-height: 34px;
  color: #031014;
  background: #69e7dc;
  border: 0;
  border-radius: 9px;
  font-size: 12px;
  font-weight: 600;
}

.channel-card--blue .buy-column button {
  color: #061426;
  background: #8ec1ff;
}

.channel-card--violet .buy-column button {
  color: #100b24;
  background: #b8a3ff;
}

.buy-column span {
  color: #7f91a8;
  font-size: 10px;
  white-space: nowrap;
}

.channel-meta {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 6px;
  margin-top: 14px;
  padding-top: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.07);
}

.channel-meta span {
  display: grid;
  grid-template-columns: 18px minmax(0, 1fr);
  gap: 0 4px;
  align-items: center;
  min-width: 0;
  color: #7588a0;
  font-size: 10px;
}

.channel-meta svg {
  grid-row: 1 / span 2;
  color: #69e7dc;
}

.channel-card--blue .channel-meta svg {
  color: #8ec1ff;
}

.channel-card--violet .channel-meta svg {
  color: #b8a3ff;
}

.channel-meta small,
.channel-meta b {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.channel-meta b {
  color: #cbd5e1;
  font-size: 10px;
  font-style: normal;
  font-weight: 500;
}

.stars {
  display: inline-flex;
  gap: 1px;
}

.stars i {
  color: #3a475a;
  font-style: normal;
  line-height: 1;
}

.stars i.filled {
  color: #69e7dc;
}

.channel-card--blue .stars i.filled {
  color: #8ec1ff;
}

.channel-card--violet .stars i.filled {
  color: #b8a3ff;
}

.price-benefits {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0;
  margin-top: 13px;
  padding: 12px 0;
  color: #7f91a8;
  background: rgba(15, 23, 42, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.07);
  border-radius: 13px;
}

.price-benefits span {
  display: grid;
  justify-items: center;
  gap: 4px;
  min-width: 0;
  padding: 0 7px;
  text-align: center;
  border-right: 1px solid rgba(255, 255, 255, 0.07);
}

.price-benefits span:last-child {
  border-right: 0;
}

.price-benefits svg {
  color: #69e7dc;
}

.price-benefits b {
  color: #cbd5e1;
  font-size: 11px;
  font-weight: 500;
}

.price-benefits small {
  color: #73869d;
  font-size: 10px;
  line-height: 1.35;
}

.price-footer {
  position: sticky;
  bottom: 0;
  z-index: 50;
  display: flex;
  gap: 10px;
  align-items: center;
  justify-content: space-between;
  margin: 14px -14px 0;
  padding: 12px 14px calc(12px + env(safe-area-inset-bottom));
  background: rgba(4, 7, 17, 0.96);
  border-top: 1px solid rgba(105, 231, 220, 0.12);
  box-shadow: 0 -12px 28px rgba(0, 0, 0, 0.34);
  backdrop-filter: blur(14px);
}

.price-footer div {
  min-width: 0;
  color: #cbd5e1;
  font-size: 11px;
  white-space: nowrap;
}

.price-footer span {
  font-weight: 500;
}

.price-footer strong {
  margin-left: 4px;
  color: #ffc58b;
  font-size: 18px;
  font-weight: 600;
}

.price-footer small {
  display: block;
  width: fit-content;
  margin-top: 5px;
  padding: 3px 7px;
  color: #ffc58b;
  background: rgba(255, 164, 48, 0.1);
  border-radius: 6px;
  font-size: 10px;
}

.price-footer button {
  display: inline-flex;
  gap: 4px;
  align-items: center;
  justify-content: center;
  min-width: 132px;
  min-height: 42px;
  color: #031014;
  background: linear-gradient(135deg, #69e7dc, #8ec1ff);
  border: 0;
  border-radius: 12px;
  box-shadow: 0 10px 24px rgba(35, 211, 196, 0.22);
  font-size: 13px;
  font-weight: 600;
}

.purchase-backdrop {
  position: absolute;
  inset: 0;
  z-index: 120;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  padding: 16px;
  background: rgba(0, 0, 0, 0.58);
  backdrop-filter: blur(6px);
}

.purchase-sheet {
  position: relative;
  width: 100%;
  padding: 20px 16px 16px;
  color: #e8f1fb;
  background: #0b0f17;
  border: 1px solid rgba(105, 231, 220, 0.14);
  border-radius: 16px;
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.38);
}

.purchase-sheet h2 {
  margin: 0 0 12px;
  color: #ffffff;
  font-size: 16px;
  font-weight: 600;
}

.purchase-sheet p {
  margin: 7px 0;
  color: #9fb0c4;
  font-size: 13px;
}

.purchase-close {
  position: absolute;
  top: 11px;
  right: 11px;
  display: grid;
  width: 30px;
  height: 30px;
  place-items: center;
  color: #8da0b7;
  background: transparent;
  border: 0;
}

.purchase-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-top: 18px;
}

.purchase-actions button {
  min-height: 40px;
  border-radius: 9px;
  font-size: 12px;
  font-weight: 600;
}

.cancel-button {
  color: #b7c9dd;
  background: rgba(255, 255, 255, 0.07);
  border: 0;
}

.continue-button {
  color: #031014;
  background: #69e7dc;
  border: 0;
}

.purchase-success {
  margin-top: 18px !important;
  color: #69e7dc !important;
  font-weight: 600;
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
</style>
