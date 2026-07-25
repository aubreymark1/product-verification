<script setup lang="ts">
import { ref } from 'vue'

const showChannelsModal = ref(false)

const channels = [
  { platform: '天猫旗舰店', price: '￥329', tag: '券后秒杀' },
  { platform: '京东自营', price: '￥339', tag: '百亿补贴' },
  { platform: '抖音电商', price: '￥319', tag: '直播专享低价' },
  { platform: '拼多多官方', price: '￥299', tag: '多人拼团' },
]

function openModal() {
  showChannelsModal.value = true
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
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="9" cy="21" r="1"></circle>
            <circle cx="20" cy="21" r="1"></circle>
            <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"></path>
          </svg>
        </div>
        <div class="text-group">
          <div class="title-row">
            <span class="main-title">查看全网低价</span>
            <span class="arrow-sym">&gt;</span>
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
          <button class="close-btn" @click="closeModal">✕</button>
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
  background: linear-gradient(135deg, rgba(88, 28, 135, 0.7), rgba(30, 64, 175, 0.7));
  border: 1.5px solid rgba(168, 85, 247, 0.5);
  border-radius: 10px;
  padding: 14px 16px;
  cursor: pointer;
  box-shadow: 0 8px 24px rgba(126, 34, 206, 0.35);
  transition: all 0.2s ease;
}

.purple-glow-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 32px rgba(126, 34, 206, 0.5);
  border-color: rgba(168, 85, 247, 0.8);
}

.card-left-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.cart-icon-box {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  background: linear-gradient(135deg, #7c3aed, #2563eb);
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
  font-weight: 700;
  color: #ffffff;
}

.arrow-sym {
  font-size: 13px;
  color: #c084fc;
}

.sub-title {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.7);
  margin-top: 2px;
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
  font-weight: 700;
  padding: 2px 5px;
  border-radius: 4px;
  color: #ffffff;
}

.tmall { background: #ff0036; }
.xianyu { background: #00b2ff; }
.tiktok { background: #161823; }
.pdd { background: #e02e24; }

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
}

.demo-tag {
  font-size: 10px;
  color: #64748b;
}

.close-btn {
  background: none;
  border: none;
  color: #64748b;
  font-size: 16px;
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
  font-size: 10px;
  color: #38bdf8;
}

.item-price {
  display: flex;
  align-items: center;
  gap: 8px;
}

.price-val {
  font-size: 15px;
  font-weight: 700;
  color: #f43f5e;
}

.buy-btn {
  background: #2563eb;
  border: none;
  color: white;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 11px;
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
  cursor: pointer;
}
</style>
