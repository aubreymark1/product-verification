<script setup lang="ts">
import { ref } from 'vue'
import { ChevronRight, ShoppingCart, X } from 'lucide-vue-next'
import { useRouter } from 'vue-router'

const router = useRouter()
const showChannelsModal = ref(false)

const emit = defineEmits<{
  navigate: []
}>()

const channels = [
  { platform: '天猫旗舰店', price: '￥329', tag: '券后秒杀' },
  { platform: '京东自营', price: '￥339', tag: '百亿补贴' },
  { platform: '抖音电商', price: '￥319', tag: '直播专享低价' },
  { platform: '拼多多官方', price: '￥299', tag: '多人拼团' },
]

function openModal() {
  emit('navigate')
  router.push('/price-comparison')
}

function closeModal() {
  showChannelsModal.value = false
}
</script>

<template>
  <div class="multi-channel-container">
    <!-- Gradient Glow Banner Card (Matching Screenshot) -->
    <div class="purple-glow-card" @click="openModal">
      <div class="card-left-section">
        <div class="cart-icon-box">
          <ShoppingCart :size="19" :stroke-width="1.8" />
        </div>
        <div class="text-group">
          <div class="title-row">
            <span class="main-title">查看全网低价</span>
            <ChevronRight class="arrow-sym" :size="15" :stroke-width="1.8" />
          </div>
          <span class="sub-title">汇总多渠道价格，帮你省更多</span>
        </div>
      </div>

      <div class="card-right-section">
        <div class="platform-badges-row">
          <span class="badge tmall">天猫</span>
          <span class="badge xianyu">得物</span>
          <span class="badge tiktok">抖音</span>
          <span class="badge pdd">拼多</span>
        </div>
        <span class="summary-text">已汇总 12 个渠道低价</span>
      </div>
    </div>

    <!-- Modal -->
    <div v-if="showChannelsModal" class="modal-backdrop" @click.self="closeModal">
      <div class="channel-modal">
        <div class="modal-header">
          <div>
            <h3>全网比价汇总 (12个渠道)</h3>
            <span class="demo-tag">演示数据，仅用于功能展示</span>
          </div>
          <button class="close-btn" aria-label="关闭" @click="closeModal">
            <X :size="18" :stroke-width="1.8" />
          </button>
        </div>

        <div class="channel-list">
          <div v-for="c in channels" :key="c.platform" class="channel-item">
            <div class="item-meta">
              <span class="platform-name">{{ c.platform }}</span>
              <span class="tag-chip">{{ c.tag }}</span>
            </div>
            <div class="item-price">
              <span class="price-val">{{ c.price }}</span>
              <button class="buy-btn" @click="closeModal">前往</button>
            </div>
          </div>
        </div>

        <button class="modal-close-bar" @click="closeModal">返回验真结果</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.multi-channel-container {
  width: 100%;
}

.purple-glow-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background:
    radial-gradient(circle at 0% 50%, rgba(98, 80, 255, 0.16), transparent 42%),
    rgba(13, 24, 38, 0.82);
  border: 1px solid rgba(132, 112, 255, 0.24);
  border-radius: 14px;
  padding: 16px 12px;
  cursor: pointer;
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.035),
    0 8px 18px rgba(0, 0, 0, 0.14);
  transition: all 0.2s ease;
}

.purple-glow-card:hover {
  background: rgba(18, 31, 49, 0.88);
  border-color: rgba(132, 112, 255, 0.32);
}

.card-left-section {
  display: flex;
  align-items: center;
  gap: 10px;
}

.cart-icon-box {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: transparent;
  border: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
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

.main-title {
  font-size: 15px;
  font-weight: 500;
  color: #ffffff;
}

.arrow-sym {
  color: #c084fc;
}

.sub-title {
  font-size: 11px;
  font-weight: 400;
  color: rgba(255, 255, 255, 0.52);
  margin-top: 6px;
}

.card-right-section {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
}

.platform-badges-row {
  display: flex;
  gap: 4px;
}

.badge {
  font-size: 9px;
  font-weight: 500;
  padding: 2px 5px;
  border-radius: 4px;
  color: #ffffff;
}

.tmall { background: rgba(255, 72, 92, 0.52); }
.xianyu { background: rgba(90, 167, 255, 0.42); }
.tiktok { background: rgba(255, 255, 255, 0.08); }
.pdd { background: rgba(255, 72, 92, 0.44); }

.summary-text {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.6);
}

/* Modal */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(10, 15, 29, 0.85);
  backdrop-filter: blur(6px);
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.channel-modal {
  width: 100%;
  max-width: 420px;
  background: #0f172a;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 18px;
  color: white;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.modal-header h3 {
  margin: 0 0 2px;
  font-size: 15px;
  font-weight: 600;
}

.demo-tag {
  font-size: 11px;
  font-weight: 400;
  color: #64748b;
}

.close-btn {
  width: 32px;
  height: 32px;
  display: grid;
  place-items: center;
  background: none;
  border: none;
  color: #64748b;
  cursor: pointer;
}

.channel-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.channel-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  background: rgba(30, 41, 59, 0.5);
  border-radius: 8px;
}

.item-meta {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.platform-name {
  font-size: 13px;
  font-weight: 600;
}

.tag-chip {
  font-size: 12px;
  font-weight: 400;
  color: #38bdf8;
}

.item-price {
  display: flex;
  align-items: center;
  gap: 8px;
}

.price-val {
  font-size: 15px;
  font-weight: 600;
  color: #f43f5e;
}

.buy-btn {
  background: #2563eb;
  border: none;
  color: white;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 500;
  cursor: pointer;
}

.modal-close-bar {
  width: 100%;
  padding: 8px;
  background: rgba(255, 255, 255, 0.06);
  border: none;
  border-radius: 8px;
  color: #94a3b8;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
}
</style>
